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


def _iter_target_sites(session: SessionLocal, ids: Iterable[int] | None):
    query = session.query(Site)
    if ids:
        return query.filter(Site.id.in_(ids)).all()
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
    args = parser.parse_args()

    session = SessionLocal()
    try:
        targets = _iter_target_sites(session, args.site_ids)
        if not targets:
            print("No hay sitios publicados para republicar")
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
