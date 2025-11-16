"""Utilidad CLI para verificar el sitio publicado y los códigos HTTP clave.

Ejemplo de uso:
    python scripts/site_status_verifier.py \
        --site-url https://ReconvencionLaboralGuajira.github.io/sitio-qa-curl-4/ \
        --api-base http://127.0.0.1:8000 \
        --email mariomontero942@gmail.com \
        --password M@rio1027
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Iterable

import requests

STATUS_TARGETS = (
    ("200", "/", 200),
    ("404", "/ruta-que-no-existe", 404),
)


class VerificationError(Exception):
    """Se lanza cuando una verificación no obtiene el estado esperado."""


def _request(url: str) -> requests.Response:
    response = requests.get(url, timeout=30)
    return response


def verify_site(site_url: str) -> list[dict]:
    """Ejecuta verificaciones 200/404 contra el sitio publicado."""
    site_url = site_url.rstrip("/")
    results = []

    for label, path, expected in STATUS_TARGETS:
        start = time.perf_counter()
        response = _request(f"{site_url}{path}")
        elapsed = time.perf_counter() - start
        entry = {
            "label": label,
            "url": response.url,
            "status": response.status_code,
            "expected": expected,
            "elapsed_ms": round(elapsed * 1000, 2),
            "ok": response.status_code == expected,
            "bytes": len(response.content),
        }
        results.append(entry)
    return results


def get_token(api_base: str, email: str, password: str) -> str:
    response = requests.post(
        f"{api_base}/api/login",
        data={"username": email, "password": password},
        timeout=15,
    )
    if response.status_code != 200:
        raise VerificationError(
            f"No fue posible obtener token ({response.status_code}): {response.text}"
        )
    return response.json().get("access_token", "")


def verify_api_statuses(api_base: str, token: str, statuses: Iterable[int]) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    reports = []
    for status in statuses:
        resp = requests.get(
            f"{api_base}/api/qa/http-status/{status}", headers=headers, timeout=15
        )
        reports.append(
            {
                "requested": status,
                "status": resp.status_code,
                "ok": resp.status_code == status,
                "detail": resp.text,
            }
        )
    return reports


def print_report(site_results: list[dict], api_results: list[dict]) -> None:
    print("\n📡 Resultados del sitio publicado")
    for res in site_results:
        status_icon = "✅" if res["ok"] else "⚠️"
        print(
            f"  {status_icon} {res['label']} -> {res['status']} "
            f"({res['elapsed_ms']} ms, {res['bytes']} bytes) :: {res['url']}"
        )

    print("\n🛡️  Resultados del endpoint QA")
    for res in api_results:
        status_icon = "✅" if res["ok"] else "⚠️"
        print(
            f"  {status_icon} solicitado {res['requested']} => "
            f"recibido {res['status']} | detalle: {res['detail']}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verificador de estado publicado y API QA",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--site-url", required=True, help="URL público del sitio desplegado")
    parser.add_argument(
        "--api-base",
        default=os.getenv("API_BASE_URL", "http://127.0.0.1:8000"),
        help="URL base del backend FastAPI",
    )
    parser.add_argument(
        "--email",
        default=os.getenv("ADMIN_EMAIL"),
        help="Email admin para autenticarse (usa ADMIN_EMAIL si está presente)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("ADMIN_PASSWORD"),
        help="Password admin (o ADMIN_PASSWORD)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.email or not args.password:
        raise SystemExit("Debes definir --email y --password o las variables ADMIN_EMAIL/ADMIN_PASSWORD")

    site_results = verify_site(args.site_url)

    try:
        token = get_token(args.api_base, args.email, args.password)
    except VerificationError as exc:
        print(f"❌ Error autenticando: {exc}")
        sys.exit(1)

    api_results = verify_api_statuses(args.api_base, token, (200, 404, 500))
    print_report(site_results, api_results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario")