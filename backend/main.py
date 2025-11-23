from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
import re
import shutil
import time
import uuid
import unicodedata
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DEFAULT_TIMEZONE = os.getenv("TIMEZONE", "America/Bogota")
if DEFAULT_TIMEZONE:
    os.environ["TZ"] = DEFAULT_TIMEZONE
    try:
        time.tzset()
    except AttributeError:
        # Sistemas como Windows no exponen tzset
        pass

# Agregar el directorio raíz del proyecto al path para permitir importaciones absolutas
import sys
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar módulos locales
from backend.database import get_db, Role, Site, User, Visit, init_db
from backend.auth import (
    authenticate_user,
    build_user_claims,
    create_access_token,
    generate_temporary_password,
    get_current_user,
    hash_password,
    require_owner_of_site,
    require_superadmin,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from backend.api_schemas import UserCreate, UserPasswordUpdate, UserUpdate
from backend.utils.github_api import GitHubPublisher
from backend.utils.template_engine import TemplateEngine
from backend.utils.asset_manager import ensure_local_asset
from backend.template_helpers import normalize_drive_image, normalize_local_asset
from backend.services.user_service import OWNER_ROLE, SUPERADMIN_ROLE, serialize_user
from backend.routers.users import router as users_router
from backend.routers.roles import router as roles_router

# Inicializar app
app = FastAPI(
    title="Control de Sitios Productivos",
    description="Panel de control para gestionar sitios web de negocios",
    version="1.0.0"
)

app.include_router(users_router)
app.include_router(roles_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
frontend_path = Path(__file__).parent.parent / "frontend"
uploads_path = Path(__file__).parent.parent / "uploads"
uploads_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=frontend_path / "static"), name="static")
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
app.mount("/images", StaticFiles(directory=uploads_path), name="images")

templates = Jinja2Templates(directory=str(frontend_path))
templates.env.globals["normalize_drive_image"] = normalize_drive_image

# Inicializar servicios
template_engine = TemplateEngine()

# Cargar datos semilla y modelos de negocio
with open(Path(__file__).parent / "seed_data.json", 'r', encoding='utf-8') as f:
    SEED_DATA = json.load(f)

with open(Path(__file__).parent / "models.json", 'r', encoding='utf-8') as f:
    BUSINESS_MODELS = json.load(f)

MODEL_REGISTRY = {
    model["id"]: model for model in BUSINESS_MODELS.get("models", []) if model.get("id")
}

# Conjunto de modelos válidos detectados en el catálogo o en los datos semilla
AVAILABLE_MODEL_IDS = set(MODEL_REGISTRY.keys()) or set(SEED_DATA.keys())


OWNER_EMAIL_DOMAIN = os.getenv("OWNER_EMAIL_DOMAIN", "owners.webcontrol.local")
DEFAULT_CNAME_TARGET = os.getenv(
    "DEFAULT_CNAME_TARGET",
    "reconvencionlaboralguajira.github.io",
)
PUBLISH_INFO_MESSAGE = (
    "⏳ GitHub Pages puede tardar entre 1 y 3 minutos en activarse. "
    "Si ves un error 404 espera un momento y vuelve a recargar."
)


class PublishPipelineError(Exception):
    """Error controlado durante el pipeline de publicación."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


def _slugify_identifier(value: str, fallback: str = "owner") -> str:
    value = value or fallback
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return cleaned or fallback


def _generate_unique_username(db: Session, base_value: str) -> str:
    base = _slugify_identifier(base_value)
    username = base
    counter = 1
    while db.query(User).filter(User.username == username).first():
        counter += 1
        username = f"{base}-{counter}"
    return username


def _generate_unique_owner_email(db: Session, base_username: str) -> str:
    email = f"{base_username}@{OWNER_EMAIL_DOMAIN}"
    counter = 1
    while db.query(User).filter(User.email == email).first():
        counter += 1
        email = f"{base_username}-{counter}@{OWNER_EMAIL_DOMAIN}"
    return email


def _create_owner_account(db: Session, site: Site) -> dict:
    owner_role = db.query(Role).filter(Role.name == OWNER_ROLE).first()
    if owner_role is None:
        raise HTTPException(status_code=500, detail="No existe el rol owner para asignar al sitio")

    base_username = _slugify_identifier(site.name, fallback=f"site-{site.id}")
    username = _generate_unique_username(db, base_username)
    email = _generate_unique_owner_email(db, username)
    temporary_password = generate_temporary_password()
    hashed_password = hash_password(temporary_password)

    owner_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        plain_password=temporary_password,
        role_id=owner_role.id,
        site_id=site.id,
        activated_at=datetime.utcnow(),
    )
    db.add(owner_user)
    db.commit()
    db.refresh(owner_user)

    return {
        "user": owner_user,
        "temporary_password": temporary_password,
    }


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def _ensure_not_last_superadmin(db: Session, user: User):
    if not user.role or user.role.name != SUPERADMIN_ROLE:
        return
    superadmins = (
        db.query(User)
        .join(Role)
        .filter(Role.name == SUPERADMIN_ROLE, User.id != user.id, User.is_active == True)
        .count()
    )
    if superadmins == 0:
        raise HTTPException(status_code=400, detail="Debe existir al menos un superadmin activo")


def _apply_password(user: User, new_password: str):
    user.hashed_password = hash_password(new_password)
    user.plain_password = new_password


def _canonicalize_asset_value(value):
    if value is None:
        return ""
    if isinstance(value, str):
        cleaned = normalize_local_asset(value)
        return normalize_drive_image(cleaned)
    return value


def _coerce_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value or "[]")
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            return []
    return []


def _canonicalize_gallery(value):
    gallery_items = []
    for item in _coerce_list(value):
        gallery_items.append(_canonicalize_asset_value(item))
    return gallery_items


def _canonicalize_products(value):
    products = []
    for item in _coerce_list(value):
        if not isinstance(item, dict):
            continue
        entry = item.copy()
        entry["image"] = _canonicalize_asset_value(entry.get("image"))
        products.append(entry)
    return products


def _preferred_repo_name(site_payload: dict) -> str:
    existing = site_payload.get("github_repo")
    if existing:
        return existing
    base_name = site_payload.get("name") or f"sitio-{site_payload.get('id')}"
    normalized = unicodedata.normalize("NFKD", base_name).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9-]", "-", normalized.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        slug = f"sitio-{site_payload.get('id')}"
    return f"{slug}-{site_payload.get('id')}".strip("-")


def _serialize_site_for_publish(site: Site) -> dict:
    return {
        "id": site.id,
        "name": site.name,
        "description": site.description,
        "model_type": site.model_type,
        "hero_title": site.hero_title,
        "hero_subtitle": site.hero_subtitle,
        "hero_image": site.hero_image,
        "about_text": site.about_text,
        "about_image": site.about_image,
        "contact_email": site.contact_email,
        "contact_phone": site.contact_phone,
        "contact_address": site.contact_address,
        "whatsapp_number": site.whatsapp_number,
        "facebook_url": site.facebook_url,
        "instagram_url": site.instagram_url,
        "tiktok_url": site.tiktok_url,
        "logo_url": site.logo_url,
        "primary_color": site.primary_color,
        "secondary_color": site.secondary_color,
        "products_raw": site.products_json,
        "gallery_raw": site.gallery_images,
        "github_repo": site.github_repo,
        "custom_domain": site.custom_domain,
    }


def _execute_publish_pipeline(site_payload: dict) -> dict:
    try:
        publisher = GitHubPublisher()
    except ValueError as exc:
        raise PublishPipelineError(str(exc), status_code=400) from exc
    except Exception as exc:
        raise PublishPipelineError(str(exc), status_code=500) from exc

    desired_repo = _preferred_repo_name(site_payload)
    repo_result = publisher.create_repository(
        repo_name=desired_repo,
        description=site_payload.get("description") or ""
    )

    if not repo_result.get("success"):
        raise PublishPipelineError(repo_result.get("error", "Error al crear repositorio"))

    repo_name = repo_result["repo_name"]

    gallery_items = _coerce_list(site_payload.get("gallery_raw") or [])
    products_items = _coerce_list(site_payload.get("products_raw") or [])

    site_data = {
        "id": site_payload.get("id"),
        "name": site_payload.get("name"),
        "description": site_payload.get("description"),
        "hero_title": site_payload.get("hero_title"),
        "hero_subtitle": site_payload.get("hero_subtitle"),
        "hero_image": site_payload.get("hero_image"),
        "about_text": site_payload.get("about_text"),
        "about_image": site_payload.get("about_image"),
        "contact_email": site_payload.get("contact_email"),
        "contact_phone": site_payload.get("contact_phone"),
        "contact_address": site_payload.get("contact_address"),
        "whatsapp_number": site_payload.get("whatsapp_number"),
        "facebook_url": site_payload.get("facebook_url"),
        "instagram_url": site_payload.get("instagram_url"),
        "tiktok_url": site_payload.get("tiktok_url"),
        "logo_url": site_payload.get("logo_url"),
        "primary_color": site_payload.get("primary_color"),
        "secondary_color": site_payload.get("secondary_color"),
        "products": products_items,
        "products_json": json.dumps(products_items),
        "gallery_images": gallery_items,
    }

    asset_updates = {}
    gallery_update = None
    products_update = None

    site_data["hero_image"], changed = _localize_asset_for_publish(site_data["hero_image"])
    if changed:
        asset_updates["hero_image"] = site_data["hero_image"]

    site_data["about_image"], changed = _localize_asset_for_publish(site_data["about_image"])
    if changed:
        asset_updates["about_image"] = site_data["about_image"]

    site_data["logo_url"], changed = _localize_asset_for_publish(site_data["logo_url"])
    if changed:
        asset_updates["logo_url"] = site_data["logo_url"]

    localized_gallery, gallery_changed = _localize_gallery_for_publish(gallery_items)
    site_data["gallery_images"] = localized_gallery
    if gallery_changed:
        gallery_update = localized_gallery

    localized_products, products_changed = _localize_products_for_publish(products_items)
    site_data["products"] = localized_products
    site_data["products_json"] = json.dumps(localized_products)
    if products_changed:
        products_update = localized_products

    site_files = template_engine.generate_site(site_payload["model_type"], site_data)

    publish_result = publisher.publish_site(
        repo_name=repo_name,
        site_files=site_files,
        custom_domain=site_payload.get("custom_domain"),
    )

    if not publish_result.get("success"):
        raise PublishPipelineError(publish_result.get("error", "Error al publicar sitio"))

    return {
        "repo_name": repo_name,
        "pages_url": publish_result.get("pages_url"),
        "warning": publish_result.get("warning"),
        "asset_updates": asset_updates,
        "gallery_update": gallery_update,
        "products_update": products_update,
    }


def _get_preview_image(site):
    hero_image = _canonicalize_asset_value(getattr(site, "hero_image", ""))
    if hero_image:
        return hero_image

    raw_gallery = getattr(site, "gallery_images", "") or "[]"
    try:
        parsed_gallery = json.loads(raw_gallery) if isinstance(raw_gallery, str) else raw_gallery
    except json.JSONDecodeError:
        parsed_gallery = []

    for item in _coerce_list(parsed_gallery):
        normalized = _canonicalize_asset_value(item)
        if normalized:
            return normalized

    return _canonicalize_asset_value(getattr(site, "logo_url", ""))


def _localize_asset_for_publish(value):
    canonical = _canonicalize_asset_value(value)
    if not canonical:
        return canonical, False
    if canonical.startswith("images/"):
        return canonical, False
    local_path, downloaded = ensure_local_asset(canonical)
    if local_path and local_path != canonical:
        return local_path, True
    return canonical, False


def _localize_gallery_for_publish(value):
    gallery_items = []
    changed = False
    for item in _coerce_list(value):
        localized, was_downloaded = _localize_asset_for_publish(item)
        gallery_items.append(localized)
        if was_downloaded:
            changed = True
    return gallery_items, changed


def _localize_products_for_publish(value):
    products = []
    changed = False
    for item in _coerce_list(value):
        if not isinstance(item, dict):
            continue
        entry = item.copy()
        localized, was_downloaded = _localize_asset_for_publish(entry.get("image"))
        entry["image"] = localized
        products.append(entry)
        if was_downloaded:
            changed = True
    return products, changed


def _inline_preview_assets(html: str, generated_files: dict) -> str:
    """Incrusta assets críticos (CSS/JS) en la vista previa para evitar 404 en el editor."""
    css = generated_files.get("styles.css")
    if css:
        html = re.sub(r'<link[^>]+href=["\'](?:\./)?styles\.css["\'][^>]*>\s*', "", html, flags=re.IGNORECASE)
        style_tag = f"<style>\n{css}\n</style>"
        if "</head>" in html:
            html = html.replace("</head>", f"{style_tag}</head>", 1)
        else:
            html = style_tag + html

    script = generated_files.get("tracking.js")
    if script:
        html = re.sub(r'<script[^>]+src=["\'](?:\./)?tracking\.js["\'][^>]*></script>\s*', "", html, flags=re.IGNORECASE)
        script_tag = f"<script>\n{script}\n</script>"
        if "</body>" in html:
            html = html.replace("</body>", f"{script_tag}</body>", 1)
        else:
            html = html + script_tag

    return html

# ============= FEATURE FLAGS =============
# Habilitar GPT-5 para todos los clientes (controlado por ENV, por defecto true)
GPT5_ENABLED = os.getenv("GPT5_ENABLED", "true").lower() in ("1", "true", "yes", "on")


# ============= RUTAS FRONTEND =============

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login-windster.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Panel principal - Windster version"""
    context = {"request": request, "initial_view": "dashboard"}
    return templates.TemplateResponse("dashboard-windster.html", context)


@app.get("/dashboard-old", response_class=HTMLResponse)
async def dashboard_old(request: Request):
    """Panel principal - Versión original"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    """Página de modelos"""
    return templates.TemplateResponse("models-windster.html", {"request": request})

@app.get("/users-management", response_class=HTMLResponse)
async def users_management_page(request: Request):
    """Vista integrada para la gestión de usuarios y roles."""
    context = {"request": request, "initial_view": "users"}
    return templates.TemplateResponse("dashboard-windster.html", context)

@app.get("/create-site", response_class=HTMLResponse)
async def create_site_page(request: Request):
    """Página de crear sitio"""
    return templates.TemplateResponse("create-site-windster.html", {"request": request})


@app.get("/editor/{site_id}", response_class=HTMLResponse)
async def editor_page(site_id: int, request: Request):
    """Página de editor"""
    return templates.TemplateResponse("editor-visual.html", {"request": request, "site_id": site_id})


# ============= API AUTH =============

@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login con username/email + password."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Registrar el último acceso para que aparezca en el panel de usuarios
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    claims = build_user_claims(user)
    access_token = create_access_token(data=claims, expires_delta=access_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }


@app.get("/api/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario autenticado."""
    data = serialize_user(current_user)
    return data


# ============= API FLAGS =============

@app.get("/api/flags")
async def get_flags():
    """Obtener banderas de características para clientes."""
    return {
        "gpt5_enabled": GPT5_ENABLED
    }


# ============= API MODELS =============

@app.get("/api/models")
async def get_models():
    """Obtener modelos de negocio"""
    return BUSINESS_MODELS


@app.get("/api/qa/http-status/{status_code}")
async def qa_http_status(
    status_code: int,
    current_user: User = Depends(get_current_user)
):
    """Exponer respuestas controladas para auditorías HTTP."""
    if status_code == 200:
        return {"status": 200, "detail": "Respuesta de prueba 200"}
    if status_code == 404:
        raise HTTPException(status_code=404, detail="Respuesta de prueba 404 controlada")
    if status_code == 500:
        raise HTTPException(status_code=500, detail="Respuesta de prueba 500 controlada")

    raise HTTPException(
        status_code=400,
        detail="Código no soportado. Usa 200, 404 o 500"
    )

# ============= API SITES =============

@app.get("/api/sites")
async def get_sites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar sitios accesibles para el usuario actual."""
    query = db.query(Site)
    if current_user.role and current_user.role.name == OWNER_ROLE:
        if not current_user.site_id:
            return []
        query = query.filter(Site.id == current_user.site_id)
    sites = query.all()

    return [
        {
            "id": site.id,
            "name": site.name,
            "model_type": site.model_type,
            "description": site.description,
            "logo_url": _canonicalize_asset_value(site.logo_url),
            "hero_image": _canonicalize_asset_value(site.hero_image),
            "preview_image": _get_preview_image(site),
            "custom_domain": site.custom_domain,
            "cname_record": site.cname_record or DEFAULT_CNAME_TARGET,
            "github_url": site.github_url,
            "facebook_url": site.facebook_url or "",
            "instagram_url": site.instagram_url or "",
            "tiktok_url": site.tiktok_url or "",
            "whatsapp_number": site.whatsapp_number or "",
            "primary_color": site.primary_color or "",
            "secondary_color": site.secondary_color or "",
            "is_published": site.is_published,
            "created_at": site.created_at.isoformat(),
            "updated_at": site.updated_at.isoformat()
        }
        for site in sites
    ]


@app.get("/api/sites/{site_id}")
async def get_site(
    site_id: int,
    db: Session = Depends(get_db),
    _authorized_user: User = Depends(require_owner_of_site)
):
    """Obtener sitio específico"""
    site = db.query(Site).filter(Site.id == site_id).first()
	
    if not site:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")

    # Parsear JSON fields
    try:
        gallery_images = json.loads(site.gallery_images) if site.gallery_images else []
    except:
        gallery_images = []
    gallery_images = _canonicalize_gallery(gallery_images)
    
    try:
        products = json.loads(site.products_json) if site.products_json else []
    except:
        products = []
    products = _canonicalize_products(products)
    
    return {
        "id": site.id,
        "name": site.name,
        "model_type": site.model_type,
        "description": site.description,
        "custom_domain": site.custom_domain,
    "cname_record": site.cname_record or DEFAULT_CNAME_TARGET,
        "github_repo": site.github_repo,
        "github_url": site.github_url,
        "is_published": site.is_published,
        "hero_title": site.hero_title,
        "hero_subtitle": site.hero_subtitle,
    "hero_image": _canonicalize_asset_value(site.hero_image),
        "about_text": site.about_text,
    "about_image": _canonicalize_asset_value(site.about_image),
        "contact_email": site.contact_email,
        "contact_phone": site.contact_phone,
        "whatsapp_number": site.whatsapp_number,
        "contact_address": site.contact_address,
        "facebook_url": site.facebook_url,
        "instagram_url": site.instagram_url,
        "tiktok_url": site.tiktok_url,
    "logo_url": _canonicalize_asset_value(site.logo_url),
        "primary_color": site.primary_color,
        "secondary_color": site.secondary_color,
        "gallery_images": gallery_images,
        "products": products,
        "created_at": site.created_at.isoformat(),
        "updated_at": site.updated_at.isoformat()
    }


@app.post("/api/sites")
async def create_site(
    request: Request,
    db: Session = Depends(get_db),
    _superadmin: User = Depends(require_superadmin)
):
    """Crear nuevo sitio"""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="El cuerpo de la solicitud no es JSON válido")

    name = str(data.get("name", "")).strip()
    model_type = str(data.get("model_type", "")).strip()

    if not model_type:
        raise HTTPException(status_code=400, detail="Selecciona un modelo de negocio antes de crear el sitio")

    if AVAILABLE_MODEL_IDS and model_type not in AVAILABLE_MODEL_IDS:
        raise HTTPException(status_code=400, detail="El modelo seleccionado no es válido")

    if not name:
        raise HTTPException(status_code=400, detail="Ingresa el nombre del negocio")
    
    # Cargar datos semilla si existen para este tipo de modelo
    seed_data = SEED_DATA.get(model_type, {})
    
    gallery_input = data.get("gallery_images")
    if gallery_input is None:
        gallery_input = seed_data.get("gallery_images", [])
    gallery_payload = _canonicalize_gallery(gallery_input)

    products_input = (
        data.get("products")
        or data.get("products_json")
        or seed_data.get("products", [])
    )
    products_payload = _canonicalize_products(products_input)

    # Crear sitio en BD usando datos semilla como valores por defecto
    site = Site(
        name=name or seed_data.get("site_name", "Nuevo Sitio"),
        model_type=model_type,
        description=data.get("description", seed_data.get("site_description", "")),
        custom_domain=data.get("custom_domain"),
    cname_record=data.get("cname_record") or DEFAULT_CNAME_TARGET,
    hero_title=data.get("hero_title", seed_data.get("hero_title", name)),
        hero_subtitle=data.get("hero_subtitle", seed_data.get("hero_subtitle", "")),
        hero_image=_canonicalize_asset_value(data.get("hero_image", seed_data.get("hero_image", ""))),
        about_text=data.get("about_text", seed_data.get("about_text", "")),
        about_image=_canonicalize_asset_value(data.get("about_image", seed_data.get("about_image", ""))),
        contact_email=data.get("contact_email", seed_data.get("contact_email", "")),
        contact_phone=data.get("contact_phone", seed_data.get("contact_phone", "")),
        contact_address=data.get("contact_address", ""),
        whatsapp_number=data.get("whatsapp_number", seed_data.get("whatsapp_number", "")),
        facebook_url=data.get("facebook_url", seed_data.get("facebook_url", "")),
        instagram_url=data.get("instagram_url", seed_data.get("instagram_url", "")),
        tiktok_url=data.get("tiktok_url", seed_data.get("tiktok_url", "")),
        logo_url=_canonicalize_asset_value(data.get("logo_url", "")),
        primary_color=data.get("primary_color", ""),
        secondary_color=data.get("secondary_color", ""),
        gallery_images=json.dumps(gallery_payload),
        products_json=json.dumps(products_payload)
    )
    
    db.add(site)
    db.commit()
    db.refresh(site)

    owner_payload = _create_owner_account(db, site)
    owner_user = owner_payload["user"]
    owner_data = serialize_user(owner_user, include_sensitive=True)
    owner_data["temporary_password"] = owner_payload["temporary_password"]

    return {
        "id": site.id,
        "name": site.name,
        "message": "Sitio creado exitosamente con datos de ejemplo",
        "cname_record": site.cname_record,
        "owner": owner_data,
    }


@app.put("/api/sites/{site_id}")
async def update_site(
    site_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _authorized_user: User = Depends(require_owner_of_site)
):
    """Actualizar sitio"""
    site = db.query(Site).filter(Site.id == site_id).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")

    data = await request.json()

    for asset_field in ("hero_image", "about_image", "logo_url"):
        if asset_field in data:
            data[asset_field] = _canonicalize_asset_value(data[asset_field])
    
    # Actualizar campos
    for key, value in data.items():
        if key == "products" or key == "products_json":
            products_data = _canonicalize_products(value)
            setattr(site, "products_json", json.dumps(products_data))
            continue

        if key == "gallery_images":
            gallery_data = _canonicalize_gallery(value)
            setattr(site, "gallery_images", json.dumps(gallery_data))
            continue

        if hasattr(site, key) and key != "id":
            setattr(site, key, value)
    
    db.commit()
    db.refresh(site)
    
    return {
        "id": site.id,
        "message": "Sitio actualizado exitosamente"
    }


@app.post("/api/sites/preview", response_class=HTMLResponse)
async def preview_site(request: Request, _current_user: User = Depends(get_current_user)):
    """Generar una vista previa HTML en caliente para el editor visual."""
    payload = await request.json()
    model_type = payload.get("model_type")

    if not model_type:
        raise HTTPException(status_code=400, detail="model_type es requerido")

    site_data = payload.copy()
    # Asegurar defaults mínimos para evitar llaves faltantes en plantillas
    site_data.setdefault("name", "Vista previa")
    site_data.setdefault("hero_title", site_data.get("name", ""))
    site_data.setdefault("hero_subtitle", "")

    try:
        files = template_engine.generate_site(model_type, site_data)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    html = files.get("index.html", "")
    html = _inline_preview_assets(html, files)
    return HTMLResponse(content=html)


@app.delete("/api/sites/{site_id}")
async def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    _superadmin: User = Depends(require_superadmin)
):
    """Eliminar sitio"""
    site = db.query(Site).filter(Site.id == site_id).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    # Eliminar repositorio de GitHub si existe
    if site.github_repo:
        try:
            publisher = GitHubPublisher()
            publisher.delete_repository(site.github_repo)
        except:
            pass
    
    db.delete(site)
    db.commit()
    
    return {"message": "Sitio eliminado exitosamente"}

@app.post("/api/sites/{site_id}/publish")
async def publish_site(
    site_id: int,
    db: Session = Depends(get_db),
    _superadmin: User = Depends(require_superadmin)
):
    """Publicar sitio en GitHub Pages sin bloquear el event loop."""
    site = db.query(Site).filter(Site.id == site_id).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")

    site_payload = _serialize_site_for_publish(site)

    try:
        publish_output = await run_in_threadpool(_execute_publish_pipeline, site_payload)
    except PublishPipelineError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    for field, value in publish_output["asset_updates"].items():
        setattr(site, field, value)

    if publish_output["gallery_update"] is not None:
        site.gallery_images = json.dumps(publish_output["gallery_update"])

    if publish_output["products_update"] is not None:
        site.products_json = json.dumps(publish_output["products_update"])

    site.github_repo = publish_output["repo_name"]
    site.github_url = publish_output["pages_url"]
    site.is_published = True
    db.commit()

    return {
        "message": "Sitio publicado exitosamente",
        "url": site.github_url,
        "info": PUBLISH_INFO_MESSAGE,
        "warning": publish_output.get("warning"),
    }


# ============= API STATS =============

@app.get("/api/stats/{site_id}")
async def get_stats(
    site_id: int,
    db: Session = Depends(get_db),
    _authorized_user: User = Depends(require_owner_of_site)
):
    """Obtener estadísticas de un sitio"""
    site = db.query(Site).filter(Site.id == site_id).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")

    # Contar visitas totales
    total_visits = db.query(Visit).filter(Visit.site_id == site_id).count()
    
    # Visitas por día (últimos 7 días)
    from datetime import datetime, timedelta
    today = datetime.utcnow()
    visits_by_day = []
    
    for i in range(7):
        day = today - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        count = db.query(Visit).filter(
            Visit.site_id == site_id,
            Visit.timestamp >= day_start,
            Visit.timestamp <= day_end
        ).count()
        
        visits_by_day.append({
            "date": day.strftime("%Y-%m-%d"),
            "visits": count
        })
    
    return {
        "site_id": site_id,
        "site_name": site.name,
        "total_visits": total_visits,
        "visits_by_day": list(reversed(visits_by_day))
    }


@app.post("/api/stats/{site_id}/visit")
async def register_visit(
    site_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Registrar visita (llamado desde el sitio publicado)"""
    data = await request.json()
    
    visit = Visit(
        site_id=site_id,
        ip_address=request.client.host,
        user_agent=data.get("userAgent", ""),
        referer=data.get("referrer", "")
    )
    
    db.add(visit)
    db.commit()
    
    return {"message": "Visita registrada"}




@app.get("/api/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Estadísticas del dashboard según el rol."""
    from sqlalchemy import func

    if current_user.role and current_user.role.name == OWNER_ROLE:
        if not current_user.site_id:
            return {"total_sites": 0, "published_sites": 0, "total_visits": 0, "top_sites": []}
        site = db.query(Site).filter(Site.id == current_user.site_id).first()
        if not site:
            return {"total_sites": 0, "published_sites": 0, "total_visits": 0, "top_sites": []}
        visit_count = db.query(Visit).filter(Visit.site_id == site.id).count()
        return {
            "total_sites": 1,
            "published_sites": 1 if site.is_published else 0,
            "total_visits": visit_count,
            "top_sites": [{"id": site.id, "name": site.name, "visits": visit_count}],
        }

    total_sites = db.query(Site).count()
    published_sites = db.query(Site).filter(Site.is_published == True).count()
    total_visits = db.query(Visit).count()
    top_sites = db.query(
        Site.id,
        Site.name,
        func.count(Visit.id).label('visit_count')
    ).outerjoin(Visit, Site.id == Visit.site_id)\
     .group_by(Site.id)\
     .order_by(func.count(Visit.id).desc())\
     .limit(5)\
     .all()

    return {
        "total_sites": total_sites,
        "published_sites": published_sites,
        "total_visits": total_visits,
        "top_sites": [
            {
                "id": site.id,
                "name": site.name,
                "visits": site.visit_count
            }
            for site in top_sites
        ]
    }


# ============= API UPLOAD =============

@app.post("/api/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    site_id: int = None,
    current_user: User = Depends(get_current_user)
):
    """
    Subir imagen al servidor y retornar la URL relativa.
    La imagen se guardará en uploads/ y se subirá al repo de GitHub al publicar.
    """
    if current_user.role and current_user.role.name == OWNER_ROLE:
        if site_id is None or current_user.site_id != site_id:
            raise HTTPException(status_code=403, detail="Solo puedes subir imágenes para tu sitio")

    # Validar tipo de archivo
    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Usa: JPG, PNG, GIF, WebP o SVG"
        )
    
    # Validar tamaño (máximo 5MB)
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    temp_file = await file.read()
    file_size = len(temp_file)
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=400,
            detail="La imagen es muy grande. Tamaño máximo: 5MB"
        )
    
    try:
        # Generar nombre único
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Crear carpeta uploads si no existe
        uploads_dir = Path(__file__).parent.parent / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        
        # Guardar archivo
        file_path = uploads_dir / unique_filename
        with open(file_path, "wb") as buffer:
            buffer.write(temp_file)
        
        # Retornar URL relativa (será subida al repo después)
        return {
            "success": True,
            "filename": unique_filename,
            "url": f"/images/{unique_filename}",
            "local_path": str(file_path),
            "size": file_size,
            "type": file.content_type
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir imagen: {str(e)}"
        )


# ============= STARTUP =============

@app.on_event("startup")
async def startup_event():
    """Inicializar BD al arrancar"""
    init_db()
    print("✅ Servidor iniciado")
    print(f"📊 Panel disponible en: http://localhost:8000")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
