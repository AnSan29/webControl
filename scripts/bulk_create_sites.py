#!/usr/bin/env python3
"""Carga masiva de sitios desde un CSV y descarga logos remotos al repositorio local.

Este comando:
1. Lee el archivo ``webcontrol_pages.xlsx - Sheet1.csv`` (o el que se indique por CLI).
2. Normaliza colores, teléfonos y modelos de negocio.
3. Descarga cada logo remoto (Drive, http/https) hacia ``uploads/`` usando ``ensure_local_asset``
   para cumplir con el requerimiento de scraping/descarga previo al registro.
4. Se autentica contra la API de webControl y crea los sitios vía ``POST /api/sites``.

Ejemplo de uso:
    python scripts/bulk_create_sites.py --email admin@webcontrol.com --password admin123
"""
from __future__ import annotations

import argparse
import csv
import getpass
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import httpx
from starlette.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.template_helpers import normalize_drive_image  # pylint: disable=wrong-import-position
from backend.utils.asset_manager import ensure_local_asset  # pylint: disable=wrong-import-position

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_CSV = "webcontrol_pages.xlsx - Sheet1.csv"
MODEL_ALIASES = {
    "artesania": "artesanias",
    "artesanias": "artesanias",
    "artesanía": "artesanias",
    "ganaderia": "chivos",
    "ganadería": "chivos",
    "chivos": "chivos",
    "gastronomia": "cocina",
    "gastronomía": "cocina",
    "cocina": "cocina",
    "belleza": "belleza",
    "adecuaciones": "adecuaciones",
}

HEX_RE = re.compile(r"[0-9a-fA-F]{6}$")


@dataclass
class SiteResult:
    name: str
    status: str
    site_id: int | None = None
    detail: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Carga masiva de sitios desde CSV")
    parser.add_argument("--csv", default=DEFAULT_CSV, help="Ruta del CSV con los datos")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="URL base del backend (usa 'asgi' para ejecutar la app en memoria)",
    )
    parser.add_argument("--email", default=os.getenv("WEBCONTROL_ADMIN_EMAIL", "admin@webcontrol.com"), help="Email del administrador")
    parser.add_argument("--password", default=os.getenv("WEBCONTROL_ADMIN_PASSWORD"), help="Password del administrador")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="No crear sitios cuyos nombres ya existan")
    parser.add_argument("--no-skip-existing", dest="skip_existing", action="store_false", help="Forzar creación aunque ya exista nombre")
    parser.add_argument("--dry-run", action="store_true", help="Simula la carga sin llamar a la API ni descargar assets")
    return parser.parse_args()


def ensure_password(args: argparse.Namespace) -> str:
    if args.password:
        return args.password
    return getpass.getpass("Password de administrador: ")


def load_palette_defaults() -> Dict[str, Dict[str, str]]:
    models_file = REPO_ROOT / "backend" / "models.json"
    data = json.loads(models_file.read_text(encoding="utf-8"))
    palettes: Dict[str, Dict[str, str]] = {}
    for entry in data.get("models", []):
        palette = entry.get("palette") or {}
        palettes[entry["id"]] = {
            "primary": palette.get("primary", "#333333"),
            "secondary": palette.get("secondary", "#666666"),
        }
    return palettes


def normalize_model(raw: str | None) -> str:
    if not raw:
        return ""
    normalized = (
        unicodedata.normalize("NFKD", raw)
        .encode("ASCII", "ignore")
        .decode("ASCII")
        .lower()
        .strip()
    )
    normalized = normalized.replace(" ", "")
    return MODEL_ALIASES.get(normalized, "")


def normalize_color(raw: str | None, fallback: str) -> str:
    if not raw:
        return fallback
    cleaned = raw.upper().replace("N.º", "").replace("Nº", "").replace("NO.", "").replace("N.", "")
    cleaned = re.sub(r"[^0-9A-F]", "", cleaned)
    if len(cleaned) == 3:
        cleaned = "".join(ch * 2 for ch in cleaned)
    elif len(cleaned) < 6:
        return fallback
    elif len(cleaned) > 6:
        cleaned = cleaned[:6]
    candidate = f"#{cleaned}"
    return candidate if HEX_RE.match(cleaned) else fallback


def slugify(value: str | None) -> str:
    if not value:
        return ""
    ascii_text = (
        unicodedata.normalize("NFKD", value)
        .encode("ASCII", "ignore")
        .decode("ASCII")
        .lower()
    )
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return ascii_text


def normalize_phone(value: str | int | None) -> str:
    if value is None:
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits[:20]


def normalize_url(value: str | None) -> str:
    return (value or "").strip()


def localize_logo(raw_url: str | None, *, dry_run: bool) -> str:
    normalized = normalize_drive_image(raw_url)
    if not normalized:
        return ""
    if dry_run:
        return normalized
    localized, _downloaded = ensure_local_asset(normalized)
    return localized or normalized


def build_payload(row: Dict[str, str], palettes: Dict[str, Dict[str, str]], *, dry_run: bool) -> Tuple[Dict[str, Any], str]:
    model_type = normalize_model(row.get("modelo_negocio"))
    if not model_type:
        raise ValueError("modelo_negocio inválido o no soportado")

    defaults = palettes.get(model_type, {})
    primary_color = normalize_color(row.get("color_primario"), defaults.get("primary", "#333333"))
    secondary_color = normalize_color(row.get("color_secundario"), defaults.get("secondary", "#555555"))

    phone = normalize_phone(row.get("whatsapp"))
    contact_email = f"{slugify(row.get('nombre_negocio')) or 'contacto'}@sitiosproductivos.local"

    payload = {
        "name": (row.get("nombre_negocio") or "Sitio sin nombre").strip(),
        "model_type": model_type,
        "description": (row.get("descripcion_negocio") or "").strip(),
        "hero_title": (row.get("titulo_principal") or row.get("nombre_negocio") or "").strip(),
        "hero_subtitle": (row.get("subtitulo") or "").strip(),
        "about_text": (row.get("descripcion_negocio") or "").strip(),
        "contact_address": (row.get("ubicacion") or "").strip(),
        "contact_phone": phone,
        "whatsapp_number": phone,
        "contact_email": contact_email,
        "facebook_url": normalize_url(row.get("facebook")),
        "instagram_url": normalize_url(row.get("instagram")),
        "tiktok_url": normalize_url(row.get("tiktok")),
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "logo_url": localize_logo(row.get("logo_url"), dry_run=dry_run),
        "gallery_images": [],
        "products": [],
    }
    return payload, model_type


def create_http_client(base_url: str) -> Tuple[Any, bool]:
    normalized = base_url.strip()
    if normalized.lower() in {"asgi", "internal"}:
        from backend.main import app  # pylint: disable=import-outside-toplevel

        client = TestClient(app)
        return client, True

    client = httpx.Client(base_url=normalized.rstrip("/"))
    return client, False


def login(client: Any, email: str, password: str) -> str:
    response = client.post(
        "/api/login",
        data={"username": email, "password": password},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Login falló ({response.status_code}): {response.text}")
    data = response.json()
    return data["access_token"]


def fetch_existing_names(client: Any, token: str) -> set[str]:
    response = client.get(
        "/api/sites",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"No se pudieron listar sitios: {response.text}")
    return {entry["name"].strip().lower() for entry in response.json()}


def create_site(client: Any, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = client.post(
        "/api/sites",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Error creando sitio: {response.status_code} {response.text}")
    return response.json()


def read_csv_rows(csv_path: Path) -> List[Dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe el archivo CSV: {csv_path}")
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader]


def main() -> None:
    args = parse_args()
    password = ensure_password(args)
    csv_path = Path(args.csv)
    rows = read_csv_rows(csv_path)
    palettes = load_palette_defaults()

    client, _ = create_http_client(args.base_url)
    token = ""
    existing_names: set[str] = set()

    try:
        if not args.dry_run:
            token = login(client, args.email, password)
            if args.skip_existing:
                existing_names = fetch_existing_names(client, token)

        results: List[SiteResult] = []
        for idx, row in enumerate(rows, start=1):
            name = (row.get("nombre_negocio") or f"Sitio {idx}").strip()
            lowered_name = name.lower()
            if args.skip_existing and lowered_name in existing_names:
                results.append(SiteResult(name=name, status="skipped", detail="ya existe"))
                continue
            try:
                payload, model_type = build_payload(row, palettes, dry_run=args.dry_run)
                print(f"[{idx:02d}] Procesando '{name}' ({model_type})")
                if args.dry_run:
                    results.append(SiteResult(name=name, status="dry-run"))
                    continue
                response = create_site(client, token, payload)
                site_id = response.get("id")
                existing_names.add(lowered_name)
                results.append(SiteResult(name=name, status="created", site_id=site_id))
            except Exception as exc:  # pylint: disable=broad-except
                results.append(SiteResult(name=name, status="error", detail=str(exc)))
                print(f"   ⚠️  Error con '{name}': {exc}")

        created = sum(1 for r in results if r.status == "created")
        skipped = sum(1 for r in results if r.status == "skipped")
        errors = [r for r in results if r.status == "error"]

        print("\nResumen:")
        print(f"  Sitios procesados: {len(rows)}")
        print(f"  Creados: {created}")
        print(f"  Omitidos: {skipped}")
        print(f"  Errores: {len(errors)}")
        if errors:
            for err in errors:
                print(f"   - {err.name}: {err.detail}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
