"""Audita cada plantilla base y reporta métricas de escalabilidad/renderizado."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.utils.template_engine import TemplateEngine
MODELS_FILE = ROOT / "backend" / "models.json"
SEED_FILE = ROOT / "backend" / "seed_data.json"


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_site_payload(seed: dict, model_id: str) -> dict:
    products = seed.get("products", [])
    gallery = seed.get("gallery_images", [])

    return {
        "id": 0,
        "name": seed.get("site_name", f"Sitio Demo {model_id}"),
        "description": seed.get("site_description", ""),
        "model_type": model_id,
        "hero_title": seed.get("hero_title"),
        "hero_subtitle": seed.get("hero_subtitle"),
        "hero_image": seed.get("hero_image"),
        "about_text": seed.get("about_text"),
        "about_image": seed.get("about_image"),
        "contact_email": seed.get("contact_email"),
        "contact_phone": seed.get("contact_phone"),
        "contact_address": seed.get("contact_address", ""),
        "whatsapp_number": seed.get("whatsapp_number"),
        "facebook_url": seed.get("facebook_url"),
        "instagram_url": seed.get("instagram_url"),
        "tiktok_url": seed.get("tiktok_url"),
        "logo_url": seed.get("logo_url", ""),
        "primary_color": seed.get("primary_color", ""),
        "secondary_color": seed.get("secondary_color", ""),
        "products_json": json.dumps(products),
        "gallery_images": json.dumps(gallery),
    }


def audit_template(model_id: str, engine: TemplateEngine, payload: dict) -> dict:
    start = time.perf_counter()
    files = engine.generate_site(model_id, payload)
    elapsed = time.perf_counter() - start
    index_html = files.get("index.html", "")
    soup = BeautifulSoup(index_html, "html.parser")

    imgs = soup.select("img")
    lazy_imgs = [img for img in imgs if img.get("loading") == "lazy"]
    sections = soup.select("section")
    supporters = soup.select(".supporter-badge")
    has_viewport = bool(soup.select_one("meta[name='viewport']"))

    return {
        "model": model_id,
        "render_ms": round(elapsed * 1000, 2),
        "html_kb": round(len(index_html.encode("utf-8")) / 1024, 2),
        "sections": len(sections),
        "img_count": len(imgs),
        "lazy_ratio": round((len(lazy_imgs) / len(imgs)) * 100, 2) if imgs else 0.0,
        "supporters": len(supporters),
        "responsive": has_viewport,
    }


def main() -> None:
    models_data = _load_json(MODELS_FILE)
    seed_data = _load_json(SEED_FILE)
    engine = TemplateEngine()

    print("🚀 Auditoría de escalabilidad por plantilla\n")
    header = "{:<12} {:>8} {:>10} {:>10} {:>10} {:>10} {:>11} {:>11}".format(
        "Plantilla", "ms", "HTML (KB)", "Secciones", "#Imgs", "% Lazy", "Aliados", "Viewport"
    )
    print(header)
    print("-" * len(header))

    for model in models_data["models"]:
        model_id = model["id"]
        payload = _build_site_payload(seed_data.get(model_id, {}), model_id)
        report = audit_template(model_id, engine, payload)
        print(
            f"{report['model']:<12} {report['render_ms']:>8} {report['html_kb']:>10} "
            f"{report['sections']:>10} {report['img_count']:>10} {report['lazy_ratio']:>10}% "
            f"{report['supporters']:>11} {str(report['responsive']):>11}"
        )


if __name__ == "__main__":
    main()
