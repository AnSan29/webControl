#!/usr/bin/env python3
"""Auditoría automatizada del flujo de variables de creación de sitios.

Este script utiliza el TestClient de FastAPI para autenticar un admin, crear un
sitio completo con datos controlados, recuperar la representación almacenada y
rendir los archivos HTML/CSS resultantes usando el TemplateEngine. También
genera una matriz de verificación que indica qué campos aparecen en los
artefactos generados.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Callable, Any

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
import sys

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app
from backend.utils.template_engine import TemplateEngine

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@webcontrol.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
AUDIT_ROOT = Path("qa_artifacts")


def login(client: TestClient) -> Dict[str, str]:
    """Obtener headers de autorización para la API."""
    response = client.post(
        "/api/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def build_payload(tag: str) -> Dict:
    """Generar payload con valores únicos identificados por tag."""
    hero_title = f"Hero control {tag}"
    hero_subtitle = "Catálogo maestro de contenidos"
    about_text = (
        "Este sitio de prueba verifica que cada campo pueda viajar desde los formularios "
        "hasta la publicación final."
    )
    return {
        "model_type": "artesanias",
        "name": f"QA Control Artesanías {tag}",
        "description": "Auditoría integral del flujo de datos",
        "custom_domain": f"control-{tag}.test",
        "hero_title": hero_title,
        "hero_subtitle": hero_subtitle,
        "about_text": about_text,
        "contact_email": "control@example.com",
        "contact_phone": "+57 300 111 2233",
        "contact_address": "Carrera 7 #77-77, Bogotá",
        "whatsapp_number": "+573001112233",
        "facebook_url": "https://facebook.com/control-total",
        "instagram_url": "https://instagram.com/control-total",
        "tiktok_url": "https://tiktok.com/@controltotal",
        "logo_url": "https://picsum.photos/seed/logo-control/320/320",
        "primary_color": "#7C3AED",
        "secondary_color": "#F97316",
        "products": [
            {
                "name": f"Pulsera Identidad {tag}",
                "description": "Pieza creada para validar el flujo de productos.",
                "price": "$120.000",
                "image": "https://picsum.photos/seed/product-control/1024/768",
            }
        ],
        "gallery_images": [
            "https://picsum.photos/seed/gallery-control-1/1200/900",
            "https://picsum.photos/seed/gallery-control-2/1200/900",
        ],
    }


def generate_site_files(site_data: Dict) -> Tuple[Dict[str, str], Dict[str, Dict[str, Any]]]:
    """Generar archivos del sitio y retornar también la matriz de verificación."""
    template_data = dict(site_data)
    template_data["products_json"] = json.dumps(site_data.get("products", []), ensure_ascii=False)
    template_data["gallery_images"] = json.dumps(site_data.get("gallery_images", []), ensure_ascii=False)

    engine = TemplateEngine()
    files = engine.generate_site(site_data["model_type"], template_data)

    index_html = files.get("index.html", "")
    styles_css = files.get("styles.css", "")
    def sanitize_whatsapp(value: str | None) -> str | None:
        if not value:
            return value
        return value.replace("+", "").replace(" ", "")

    checks: List[Tuple[str, Any, str, Callable[[Any], Any] | None]] = [
        ("Nombre comercial", site_data.get("name"), index_html, None),
        ("Descripción", site_data.get("description"), index_html, None),
        ("Título hero", site_data.get("hero_title"), index_html, None),
        ("Subtítulo hero", site_data.get("hero_subtitle"), index_html, None),
        ("Texto sobre nosotros", site_data.get("about_text"), index_html, None),
        ("Correo de contacto", site_data.get("contact_email"), index_html, None),
        ("Teléfono", site_data.get("contact_phone"), index_html, None),
        ("Dirección", site_data.get("contact_address"), index_html, None),
        ("WhatsApp", site_data.get("whatsapp_number"), index_html, sanitize_whatsapp),
        ("Facebook", site_data.get("facebook_url"), index_html, None),
        ("Instagram", site_data.get("instagram_url"), index_html, None),
        ("TikTok", site_data.get("tiktok_url"), index_html, None),
        ("Color primario", site_data.get("primary_color"), styles_css + index_html, None),
        ("Color secundario", site_data.get("secondary_color"), styles_css + index_html, None),
    ]

    # Verificar productos
    for idx, product in enumerate(site_data.get("products", []), start=1):
        checks.append((f"Producto {idx}: nombre", product.get("name"), index_html, None))
        checks.append((f"Producto {idx}: descripción", product.get("description"), index_html, None))
        checks.append((f"Producto {idx}: precio", product.get("price"), index_html, None))

    # Verificar galería
    for idx, url in enumerate(site_data.get("gallery_images", []), start=1):
        checks.append((f"Galería {idx}: URL", url, index_html, None))

    verification_matrix = {}
    for (label, value, target, transform) in checks:
        normalized = transform(value) if transform else value
        found = bool(normalized) and str(normalized) in target
        verification_matrix[label] = {
            "value": value,
            "normalized": normalized,
            "found": found,
        }
    return files, verification_matrix


def main() -> None:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    tag = timestamp[-6:]

    client = TestClient(app)
    headers = login(client)

    payload = build_payload(tag)
    response = client.post("/api/sites", headers=headers, json=payload)
    response.raise_for_status()
    site_id = response.json()["id"]

    site_response = client.get(f"/api/sites/{site_id}", headers=headers)
    site_response.raise_for_status()
    site_data = site_response.json()

    files, verification_matrix = generate_site_files(site_data)

    audit_dir = AUDIT_ROOT / f"content_audit_{timestamp}"
    audit_dir.mkdir(parents=True, exist_ok=True)

    (audit_dir / "site_payload.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (audit_dir / "site_data.json").write_text(
        json.dumps(site_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (audit_dir / "verification_matrix.json").write_text(
        json.dumps(verification_matrix, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    for filename, content in files.items():
        (audit_dir / filename).write_text(content, encoding="utf-8")

    print("\n=== Auditoría completada ===")
    print(f"Sitio creado con ID: {site_id}")
    print(f"Artefactos guardados en: {audit_dir}")
    print("Campos verificados:")
    for label, result in verification_matrix.items():
        status = "OK" if result["found"] else "FALTA"
        print(f" - {label}: {status}")


if __name__ == "__main__":
    main()
