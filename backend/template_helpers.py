"""Helper functions for template rendering."""
from __future__ import annotations

from urllib.parse import parse_qs, parse_qsl, urlencode, urlparse, urlunparse

LOCAL_ASSET_HOSTS = {"localhost", "127.0.0.1"}


def _merge_query_params(url: str, new_params: dict[str, str | int]) -> str:
    """Agregar o actualizar parámetros de consulta en una URL conservando los existentes."""
    parsed = urlparse(url)
    if not parsed.scheme:
        return url

    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    for key, value in new_params.items():
        if value is None:
            continue
        query[key] = str(value)

    return urlunparse(parsed._replace(query=urlencode(query)))


def _extract_drive_id(cleaned_url: str) -> str:
    if not cleaned_url:
        return ""

    parsed = urlparse(cleaned_url)

    # Pattern: /file/d/<ID>/..
    if "/d/" in parsed.path:
        try:
            return parsed.path.split("/d/")[1].split("/")[0]
        except (IndexError, ValueError):
            return ""

    # Pattern: open?id=<ID> or uc?id=<ID>
    query = parse_qs(parsed.query)
    if "id" in query and query["id"]:
        return query["id"][0]

    # Pattern: ?fileid=<ID>
    if "fileid" in query and query["fileid"]:
        return query["fileid"][0]

    return ""


def normalize_drive_image(url: str | None) -> str:
    """Convert public Google Drive links into embeddable URLs.

    The Drive file must be shared with the permission
    "Cualquier persona con el enlace" (lector) for public access.
    """
    if not url or not isinstance(url, str):
        return ""

    cleaned = url.strip()
    if not cleaned:
        return ""

    if "drive.google.com" not in cleaned:
        return cleaned

    file_id = _extract_drive_id(cleaned)
    if not file_id:
        return cleaned

    return f"https://drive.google.com/uc?export=view&id={file_id}"


def extract_drive_id(url: str | None) -> str:
    """Public helper to expose the parsed Drive file ID."""
    if not url or not isinstance(url, str):
        return ""
    return _extract_drive_id(url.strip())


def optimize_media_url(url: str | None, *, max_width: int = 1280, quality: int = 80) -> str:
    """Normaliza y agrega parámetros de optimización a imágenes pesadas (Unsplash, Picsum, etc.)."""
    normalized = normalize_drive_image(url)
    if not normalized:
        return ""

    parsed = urlparse(normalized)
    host = parsed.netloc.lower()

    if "images.unsplash.com" in host:
        params = {
            "auto": "format",
            "fit": "max",
            "w": max_width,
            "q": quality
        }
        return _merge_query_params(normalized, params)

    if "picsum.photos" in host and "/seed/" not in parsed.path:
        height = max(1, int(max_width * 0.625))
        return f"https://picsum.photos/seed/webcontrol/{max_width}/{height}"

    return normalized


def optimize_logo_url(url: str | None, *, max_width: int = 420) -> str:
    """Genera versiones livianas (miniaturas) para logos, especialmente desde Google Drive."""
    if not url or not isinstance(url, str):
        return ""

    file_id = _extract_drive_id(url.strip())
    if file_id:
        width = max(64, min(max_width, 1024))
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w{width}"

    return normalize_drive_image(url)


def supporter_initials(label: str | None) -> str:
    """Obtiene iniciales amigables para mostrar como fallback de logos."""
    if not label:
        return "AL"

    tokens = [chunk for chunk in label.replace("_", " ").split() if chunk]
    if not tokens:
        return "AL"

    first = tokens[0][0]
    last = tokens[-1][0] if len(tokens) > 1 else (tokens[0][1] if len(tokens[0]) > 1 else tokens[0][0])
    return f"{first}{last}".upper()


def normalize_local_asset(url: str | None) -> str:
    """Quita prefijos de localhost/127 y barras iniciales para assets servidos desde /images."""
    if not url or not isinstance(url, str):
        return ""

    cleaned = url.strip()
    if not cleaned:
        return ""

    # Ya es una ruta relativa esperada
    if cleaned.startswith("images/"):
        return cleaned

    # Remover la barra inicial si apunta a /images
    if cleaned.startswith("/images/"):
        return cleaned.lstrip("/")

    try:
        parsed = urlparse(cleaned)
    except ValueError:
        return cleaned

    if not parsed.scheme:
        return cleaned

    hostname = (parsed.hostname or "").lower()
    if hostname in LOCAL_ASSET_HOSTS and parsed.path.startswith("/images/"):
        return parsed.path.lstrip("/")

    return cleaned
