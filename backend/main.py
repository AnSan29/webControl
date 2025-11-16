from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
from pathlib import Path
import json
import os
import shutil
import uuid
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio backend al path
import sys
sys.path.insert(0, str(Path(__file__).parent))

# Importar módulos locales
from database import get_db, Site, Visit, init_db
from auth import (
    authenticate_admin,
    create_access_token,
    get_current_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from utils.github_api import GitHubPublisher
from utils.template_engine import TemplateEngine
from .template_helpers import normalize_drive_image

# Inicializar app
app = FastAPI(
    title="Control de Sitios Productivos",
    description="Panel de control para gestionar sitios web de negocios",
    version="1.0.0"
)

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
app.mount("/static", StaticFiles(directory=frontend_path / "static"), name="static")
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

templates = Jinja2Templates(directory=str(frontend_path))
templates.env.globals["normalize_drive_image"] = normalize_drive_image

# Inicializar servicios
template_engine = TemplateEngine()

# Cargar modelos de negocio
with open(Path(__file__).parent / "models.json", 'r', encoding='utf-8') as f:
    BUSINESS_MODELS = json.load(f)

# Cargar datos semilla
with open(Path(__file__).parent / "seed_data.json", 'r', encoding='utf-8') as f:
    SEED_DATA = json.load(f)

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
    return templates.TemplateResponse("dashboard-windster.html", {"request": request})


@app.get("/dashboard-old", response_class=HTMLResponse)
async def dashboard_old(request: Request):
    """Panel principal - Versión original"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    """Página de modelos"""
    return templates.TemplateResponse("models-windster.html", {"request": request})


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
    """Login de administrador"""
    admin = authenticate_admin(db, form_data.username, form_data.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": admin.email
    }


@app.get("/api/me")
async def get_me(current_admin = Depends(get_current_admin)):
    """Obtener info del admin actual"""
    return {
        "email": current_admin.email,
        "id": current_admin.id
    }


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


# ============= API SITES =============

@app.get("/api/sites")
async def get_sites(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Listar todos los sitios"""
    sites = db.query(Site).all()
    
    return [
        {
            "id": site.id,
            "name": site.name,
            "model_type": site.model_type,
            "description": site.description,
            "custom_domain": site.custom_domain,
            "github_url": site.github_url,
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
    current_admin = Depends(get_current_admin)
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
    
    try:
        products = json.loads(site.products_json) if site.products_json else []
    except:
        products = []
    
    return {
        "id": site.id,
        "name": site.name,
        "model_type": site.model_type,
        "description": site.description,
        "custom_domain": site.custom_domain,
        "github_repo": site.github_repo,
        "github_url": site.github_url,
        "is_published": site.is_published,
        "hero_title": site.hero_title,
        "hero_subtitle": site.hero_subtitle,
        "hero_image": site.hero_image,
        "about_text": site.about_text,
        "about_image": site.about_image,
        "contact_email": site.contact_email,
        "contact_phone": site.contact_phone,
        "whatsapp_number": site.whatsapp_number,
        "contact_address": site.contact_address,
        "facebook_url": site.facebook_url,
        "instagram_url": site.instagram_url,
        "tiktok_url": site.tiktok_url,
        "logo_url": site.logo_url,
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
    current_admin = Depends(get_current_admin)
):
    """Crear nuevo sitio"""
    data = await request.json()
    
    model_type = data.get("model_type")
    
    # Cargar datos semilla si existen para este tipo de modelo
    seed_data = SEED_DATA.get(model_type, {})
    
    # Crear sitio en BD usando datos semilla como valores por defecto
    site = Site(
        name=data.get("name", seed_data.get("site_name", "Nuevo Sitio")),
        model_type=model_type,
        description=data.get("description", seed_data.get("site_description", "")),
        custom_domain=data.get("custom_domain"),
        hero_title=data.get("hero_title", seed_data.get("hero_title", data.get("name", ""))),
        hero_subtitle=data.get("hero_subtitle", seed_data.get("hero_subtitle", "")),
        hero_image=data.get("hero_image", seed_data.get("hero_image", "")),
        about_text=data.get("about_text", seed_data.get("about_text", "")),
        about_image=data.get("about_image", seed_data.get("about_image", "")),
        contact_email=data.get("contact_email", seed_data.get("contact_email", "")),
        contact_phone=data.get("contact_phone", seed_data.get("contact_phone", "")),
        contact_address=data.get("contact_address", ""),
        whatsapp_number=data.get("whatsapp_number", seed_data.get("whatsapp_number", "")),
        facebook_url=data.get("facebook_url", seed_data.get("facebook_url", "")),
        instagram_url=data.get("instagram_url", seed_data.get("instagram_url", "")),
        tiktok_url=data.get("tiktok_url", seed_data.get("tiktok_url", "")),
        logo_url=data.get("logo_url", ""),
        primary_color=data.get("primary_color", ""),
        secondary_color=data.get("secondary_color", ""),
        gallery_images=json.dumps(data.get("gallery_images", seed_data.get("gallery_images", []))),
        products_json=json.dumps(data.get("products", seed_data.get("products", [])))
    )
    
    db.add(site)
    db.commit()
    db.refresh(site)
    
    return {
        "id": site.id,
        "name": site.name,
        "message": "Sitio creado exitosamente con datos de ejemplo"
    }


@app.put("/api/sites/{site_id}")
async def update_site(
    site_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Actualizar sitio"""
    site = db.query(Site).filter(Site.id == site_id).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    data = await request.json()
    
    # Actualizar campos
    for key, value in data.items():
        if hasattr(site, key) and key != "id":
            if key == "products":
                setattr(site, "products_json", json.dumps(value))
            elif key == "gallery_images" and isinstance(value, list):
                setattr(site, "gallery_images", json.dumps(value))
            else:
                setattr(site, key, value)
    
    db.commit()
    db.refresh(site)
    
    return {
        "id": site.id,
        "message": "Sitio actualizado exitosamente"
    }


@app.post("/api/sites/preview", response_class=HTMLResponse)
async def preview_site(request: Request, current_admin = Depends(get_current_admin)):
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
    return HTMLResponse(content=html)


@app.delete("/api/sites/{site_id}")
async def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
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
    current_admin = Depends(get_current_admin)
):
    """Publicar sitio en GitHub Pages"""
    site = db.query(Site).filter(Site.id == site_id).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    try:
        # Inicializar publisher
        publisher = GitHubPublisher()
        
        # Nombre del repositorio (normalizar caracteres especiales)
        import unicodedata
        import re
        
        # Remover acentos y normalizar
        name_normalized = unicodedata.normalize('NFKD', site.name).encode('ASCII', 'ignore').decode('ASCII')
        # Convertir a slug válido para GitHub
        repo_name = re.sub(r'[^a-zA-Z0-9\-]', '-', name_normalized.lower())
        repo_name = re.sub(r'-+', '-', repo_name)  # Eliminar guiones múltiples
        repo_name = f"{repo_name}-{site.id}".strip('-')
        
        print(f"🏷️  Nombre del repositorio: {repo_name}")
        
        # Crear repositorio si no existe
        if not site.github_repo:
            repo_result = publisher.create_repository(
                repo_name=repo_name,
                description=site.description
            )
            
            if not repo_result["success"]:
                raise HTTPException(status_code=500, detail=repo_result["error"])
            
            site.github_repo = repo_name
        
        # Generar archivos del sitio
        site_data = {
            "id": site.id,
            "name": site.name,
            "description": site.description,
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
            "products_json": site.products_json,
            "gallery_images": site.gallery_images
        }
        
        print(f"📝 Generando sitio para modelo: {site.model_type}")
        site_files = template_engine.generate_site(site.model_type, site_data)
        print(f"✅ Archivos generados: {list(site_files.keys())}")
        
        # Publicar en GitHub Pages
        print(f"🚀 Publicando en repositorio: {site.github_repo}")
        publish_result = publisher.publish_site(
            repo_name=site.github_repo,
            site_files=site_files,
            custom_domain=site.custom_domain
        )
        
        if not publish_result["success"]:
            raise HTTPException(status_code=500, detail=publish_result["error"])
        
        # Actualizar BD
        site.github_url = publish_result["pages_url"]
        site.is_published = True
        db.commit()
        
        return {
            "message": "Sitio publicado exitosamente",
            "url": site.github_url,
            "info": "⏳ GitHub Pages puede tardar 1-3 minutos en activarse. Si ves un error 404, espera unos minutos y recarga la página.",
            "warning": publish_result.get("warning", None)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= API STATS =============

@app.get("/api/stats/{site_id}")
async def get_stats(
    site_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
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
    current_admin = Depends(get_current_admin)
):
    """Estadísticas generales del dashboard"""
    total_sites = db.query(Site).count()
    published_sites = db.query(Site).filter(Site.is_published == True).count()
    total_visits = db.query(Visit).count()
    
    # Sitios más visitados
    from sqlalchemy import func
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
    current_admin = Depends(get_current_admin)
):
    """
    Subir imagen al servidor y retornar la URL relativa.
    La imagen se guardará en uploads/ y se subirá al repo de GitHub al publicar.
    """
    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Usa: JPG, PNG, GIF o WebP"
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
