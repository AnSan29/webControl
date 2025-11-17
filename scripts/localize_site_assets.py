#!/usr/bin/env python3
"""CLI para localizar y normalizar los assets multimedia guardados en la base de datos.

Este comando recorre los registros de ``Site`` y descarga cualquier imagen remota
(Google Drive, Unsplash, etc.) hacia ``uploads/`` usando ``ensure_local_asset``.
Si un archivo se descarga correctamente, la referencia en la base de datos se actualiza
para usar la ruta relativa ``images/<hash>.ext``.

Uso:
    python scripts/localize_site_assets.py --site-id 1
    python scripts/localize_site_assets.py --all
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.database import SessionLocal, Site
from backend.template_helpers import normalize_drive_image, normalize_local_asset
from backend.utils.asset_manager import ensure_local_asset


@dataclass
class LocalizationReport:
    site_id: int
    name: str
    updated_fields: list[str] = field(default_factory=list)
    skipped_fields: list[str] = field(default_factory=list)

    def mark_updated(self, field: str) -> None:
        if field not in self.updated_fields:
            self.updated_fields.append(field)

    def mark_skipped(self, field: str) -> None:
        if field not in self.skipped_fields:
            self.skipped_fields.append(field)


def _canonicalize(value: str | None) -> str:
    if not value or not isinstance(value, str):
        return ""
    cleaned = normalize_local_asset(value)
    return normalize_drive_image(cleaned)


def _parse_json_list(raw_value) -> list:
    if isinstance(raw_value, list):
        return raw_value
    if not raw_value:
        return []
    try:
        parsed = json.loads(raw_value)
    except (json.JSONDecodeError, TypeError):
        return []
    return parsed if isinstance(parsed, list) else []


def _localize_asset(value: str | None) -> tuple[str, bool]:
    canonical = _canonicalize(value)
    if not canonical:
        return "", False
    return ensure_local_asset(canonical)


def localize_site(site: Site) -> tuple[bool, LocalizationReport]:
    """Descarga assets remotos para un sitio específico."""
    report = LocalizationReport(site_id=site.id, name=site.name)
    changed = False

    for field in ("hero_image", "about_image", "logo_url"):
        new_value, downloaded = _localize_asset(getattr(site, field, ""))
        if downloaded and new_value:
            setattr(site, field, new_value)
            report.mark_updated(field)
            changed = True
        else:
            report.mark_skipped(field)

    gallery_items = _parse_json_list(site.gallery_images)
    localized_gallery = []
    gallery_changed = False
    for item in gallery_items:
        if not isinstance(item, str):
            localized_gallery.append(item)
            continue
        new_value, downloaded = _localize_asset(item)
        localized_gallery.append(new_value or item)
        gallery_changed = gallery_changed or downloaded
    if gallery_changed:
        site.gallery_images = json.dumps(localized_gallery)
        report.mark_updated("gallery_images")
        changed = True

    products = _parse_json_list(site.products_json)
    localized_products = []
    products_changed = False
    for product in products:
        if not isinstance(product, dict):
            continue
        entry = product.copy()
        new_value, downloaded = _localize_asset(entry.get("image"))
        if downloaded and new_value:
            entry["image"] = new_value
            products_changed = True
        localized_products.append(entry)
    if products_changed:
        site.products_json = json.dumps(localized_products)
        report.mark_updated("products_json")
        changed = True

    if not gallery_changed:
        report.mark_skipped("gallery_images")
    if not products_changed:
        report.mark_skipped("products_json")

    return changed, report


def _iter_sites(session, site_ids: Iterable[int] | None):
    query = session.query(Site)
    if site_ids:
        query = query.filter(Site.id.in_(site_ids))
    return query.all()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Localiza assets remotos de los sitios y actualiza la base de datos.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--site-id",
        action="append",
        type=int,
        help="ID de sitio a procesar (puede repetirse). Si se omite, se procesan todos.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calcula los cambios sin escribir en la base de datos.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    session = SessionLocal()
    try:
        targets = _iter_sites(session, args.site_id)
        if not targets:
            print("⚠️  No se encontraron sitios para procesar")
            return

        print(f"🔍 Procesando {len(targets)} sitio(s)...")
        reports: list[LocalizationReport] = []
        for site in targets:
            changed, report = localize_site(site)
            reports.append(report)
            if changed and not args.dry_run:
                session.add(site)
                session.commit()
            elif changed and args.dry_run:
                session.rollback()

            status = "actualizado" if report.updated_fields else "sin cambios"
            print(
                f" · Sitio #{report.site_id} ({report.name}): {status}"
                f" | actualizados: {', '.join(report.updated_fields) or '—'}"
            )

        print("\nResumen:")
        for report in reports:
            print(
                f" - #{report.site_id} {report.name}: "
                f"{', '.join(report.updated_fields) or 'sin descargas nuevas'}"
            )
    finally:
        session.close()


if __name__ == "__main__":
    main()
