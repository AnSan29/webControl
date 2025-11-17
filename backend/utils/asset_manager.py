import hashlib
import mimetypes
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

import requests

UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _guess_extension(url_path: str, content_type: str | None) -> str:
    """Inferir extensión del archivo usando la URL o el header Content-Type."""
    parsed_path = Path(url_path)
    suffix = parsed_path.suffix.lower()
    if suffix and len(suffix) <= 5:
        return suffix.lstrip(".")

    if content_type:
        mime = content_type.split(";")[0].strip()
        guessed = mimetypes.guess_extension(mime)
        if guessed:
            return guessed.lstrip(".")

    return "jpg"


def _is_remote_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"}


def ensure_local_asset(url: str) -> Tuple[str, bool]:
    """
    Garantiza que una URL pública esté disponible localmente dentro de /uploads.

    Retorna una tupla (ruta_relativa, descargado).
    Si la URL ya apunta a images/ o no se puede descargar, se devuelve tal cual y descargado=False.
    """
    if not url or not isinstance(url, str):
        return "", False

    trimmed = url.strip()
    if not trimmed:
        return "", False

    if trimmed.startswith("data:"):
        return trimmed, False

    if trimmed.startswith("/images/"):
        return trimmed.lstrip("/"), False

    if trimmed.startswith("images/"):
        return trimmed, False

    if not _is_remote_url(trimmed):
        return trimmed, False

    try:
        response = requests.get(trimmed, timeout=20)
        response.raise_for_status()
    except Exception as exc:  # pylint: disable=broad-except
        print(f"⚠️ No se pudo descargar el asset remoto {trimmed}: {exc}")
        return trimmed, False

    content_type = response.headers.get("Content-Type")
    extension = _guess_extension(urlparse(trimmed).path, content_type)
    hashed = hashlib.sha1(trimmed.encode("utf-8")).hexdigest()
    filename = f"{hashed}.{extension}"
    target_path = UPLOADS_DIR / filename

    if not target_path.exists():
        try:
            target_path.write_bytes(response.content)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"⚠️ Error guardando asset {trimmed}: {exc}")
            return trimmed, False

    return f"images/{filename}", True
