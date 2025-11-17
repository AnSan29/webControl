#!/usr/bin/env python3
"""Auditor de assets multimedia mediante scraping simple.

Este script descarga un sitio público, extrae recursos (img, video, source,
link[rel=image], script, etc.) y verifica que cada URL responda con éxito.

Uso:
    python scripts/multimedia_scrape_audit.py --site-url https://usuario.github.io/sitio/
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Iterator, List
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

MAX_BYTES_DEFAULT = 512 * 1024  # 512 KB
TIMEOUT_DEFAULT = 20


@dataclass
class AssetRecord:
    tag: str
    attr: str
    raw: str
    url: str
    is_local: bool


def parse_srcset(value: str) -> list[str]:
    if not value:
        return []
    entries = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        token = chunk.split()[0]
        if token:
            entries.append(token)
    return entries


def collect_assets(html: str, base_url: str) -> list[AssetRecord]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[AssetRecord] = []
    base_host = urlparse(base_url).netloc

    def register(url_value: str | None, tag: str, attr: str) -> None:
        if not url_value:
            return
        url_value = url_value.strip()
        if not url_value or url_value.startswith("data:"):
            return
        absolute = urljoin(base_url, url_value)
        parsed = urlparse(absolute)
        is_local = parsed.netloc == "" or parsed.netloc == base_host
        records.append(AssetRecord(tag=tag, attr=attr, raw=url_value, url=absolute, is_local=is_local))

    for img in soup.find_all("img"):
        register(img.get("src"), "img", "src")
        for candidate in parse_srcset(img.get("srcset")):
            register(candidate, "img", "srcset")

    for source in soup.find_all("source"):
        register(source.get("src"), "source", "src")
        for candidate in parse_srcset(source.get("srcset")):
            register(candidate, "source", "srcset")

    for video in soup.find_all("video"):
        register(video.get("poster"), "video", "poster")
        register(video.get("src"), "video", "src")

    for link in soup.find_all("link"):
        rel = (link.get("rel") or [])
        rel = [r.lower() for r in rel]
        if any(r in ("preload", "prefetch", "image", "stylesheet", "icon") for r in rel):
            register(link.get("href"), "link", "href")

    for script in soup.find_all("script"):
        register(script.get("src"), "script", "src")

    return records


def download_snippet(url: str, *, timeout: int, max_bytes: int) -> dict:
    result: dict = {
        "url": url,
        "status": None,
        "ok": False,
        "bytes_sampled": 0,
        "content_type": None,
        "error": None,
    }
    try:
        with requests.get(url, stream=True, timeout=timeout) as response:
            result["status"] = response.status_code
            result["content_type"] = response.headers.get("Content-Type")
            total = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    total += len(chunk)
                if total >= max_bytes:
                    break
            result["bytes_sampled"] = total
            result["ok"] = response.status_code < 400
    except Exception as exc:  # pylint: disable=broad-except
        result["error"] = str(exc)
    return result


def audit_site(site_url: str, *, timeout: int, max_assets: int | None, sample_bytes: int) -> dict:
    response = requests.get(site_url, timeout=timeout)
    response.raise_for_status()
    assets = collect_assets(response.text, site_url)

    unique_map = {}
    for asset in assets:
        unique_map.setdefault(asset.url, asset)
    ordered_assets = list(unique_map.values())
    if max_assets is not None:
        ordered_assets = ordered_assets[:max_assets]

    checks = []
    for asset in ordered_assets:
        fetch = download_snippet(asset.url, timeout=timeout, max_bytes=sample_bytes)
        fetch.update({
            "tag": asset.tag,
            "attr": asset.attr,
            "raw": asset.raw,
            "is_local": asset.is_local,
        })
        checks.append(fetch)

    host_counter = Counter(urlparse(c["url"]).netloc or "(local)" for c in checks)
    failures = [c for c in checks if not c["ok"]]

    return {
        "site_url": site_url,
        "total_assets": len(assets),
        "unique_checked": len(ordered_assets),
        "host_breakdown": host_counter,
        "failures": failures,
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scraping ligero para validar assets multimedia",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--site-url", required=True, help="URL público del sitio a auditar")
    parser.add_argument("--timeout", type=int, default=TIMEOUT_DEFAULT, help="Timeout de requests en segundos")
    parser.add_argument(
        "--max-assets",
        type=int,
        default=None,
        help="Máximo de assets únicos a validar (por defecto todos)",
    )
    parser.add_argument(
        "--sample-bytes",
        type=int,
        default=MAX_BYTES_DEFAULT,
        help="Bytes máximos a descargar por asset",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        help="Ruta opcional para guardar el reporte completo en JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = audit_site(
        args.site_url,
        timeout=args.timeout,
        max_assets=args.max_assets,
        sample_bytes=args.sample_bytes,
    )

    print(f"\n📸 Auditoría multimedia de {report['site_url']}")
    print(f"Assets detectados: {report['total_assets']} | únicos verificados: {report['unique_checked']}")
    print("Hosts encontrados:")
    for host, count in report["host_breakdown"].most_common():
        print(f"  - {host}: {count}")

    if report["failures"]:
        print("\n⚠️  Assets con errores:")
        for failure in report["failures"]:
            print(
                f"  · {failure['status']} {failure['url']} ({failure['tag']}[{failure['attr']}])"
                f" :: error={failure.get('error') or 'HTTP'}"
            )
    else:
        print("\n✅ Todos los assets respondieron con estado < 400")

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"\n📝 Reporte guardado en {args.output_json}")


if __name__ == "__main__":
    main()
