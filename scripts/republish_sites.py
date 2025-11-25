"""Republish already published sites so they point to the current GitHub account."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import SessionLocal, Site
from backend.main import (  # noqa: E402  pylint: disable=wrong-import-position
    PublishPipelineError,
    _execute_publish_pipeline,  # type: ignore
    _serialize_site_for_publish,  # type: ignore
)


def _republish_site(site: Site) -> dict:
    payload = _serialize_site_for_publish(site)
    result = _execute_publish_pipeline(payload)

    for field, value in result["asset_updates"].items():
        setattr(site, field, value)

    if result["gallery_update"] is not None:
        site.gallery_images = json.dumps(result["gallery_update"])

    if result["products_update"] is not None:
        site.products_json = json.dumps(result["products_update"])

    site.github_repo = result["repo_name"]
    site.github_url = result.get("pages_url")
    site.is_published = True
    return result


def _iter_target_sites(
    session: SessionLocal,
    ids: Iterable[int] | None,
    model_type: str | None = None,
    include_unpublished: bool = False,
):
    query = session.query(Site)

    if model_type:
        query = query.filter(Site.model_type == model_type)

    if ids:
        query = query.filter(Site.id.in_(ids))
        return query.all()

    if include_unpublished:
        return query.all()

    return query.filter(Site.is_published == True).all()  # noqa: E712


def main():
    parser = argparse.ArgumentParser(description="Republish GitHub Pages sites")
    parser.add_argument(
        "--site-id",
        action="append",
        type=int,
        dest="site_ids",
        help="Specific site ID(s) to republish. Repeat flag to provide multiple.",
    )
    parser.add_argument(
        "--model-type",
        dest="model_type",
        help="Limit the republish operation to a specific modelo de negocio (artesanias, cocina, chivos, etc.)",
    )
    parser.add_argument(
        "--include-unpublished",
        action="store_true",
        help="Incluir sitios que aún no estén marcados como publicados (útil tras migraciones/importaciones)",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        targets = _iter_target_sites(
            session,
            ids=args.site_ids,
            model_type=args.model_type,
            include_unpublished=args.include_unpublished,
        )
        if not targets:
            scope = "" if not args.model_type else f" para el modelo '{args.model_type}'"
            if args.include_unpublished:
                scope += " (incluyendo no publicados)"
            print(f"No hay sitios que republicar{scope}")
            return

        print(f"Republishing {len(targets)} site(s)...")
        for site in targets:
            print(f" → Site {site.id}: {site.name}")
            try:
                result = _republish_site(site)
                session.commit()
                print(
                    f"    ✓ OK -> {site.github_url} (repo {result['repo_name']})"
                )
            except PublishPipelineError as exc:
                session.rollback()
                print(f"    ✗ PublishPipelineError: {exc}")
            except Exception as exc:  # pylint: disable=broad-except
                session.rollback()
                print(f"    ✗ Error inesperado: {exc}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
