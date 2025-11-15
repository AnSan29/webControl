"""Helper functions for template rendering."""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse


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
