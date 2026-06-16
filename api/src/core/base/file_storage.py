from pathlib import Path

from core.tools.config_tools import get_or_throw

UPLOADS_DIR = get_or_throw("UPLOADS_DIR")


def save_file(file_bytes: bytes, filename: str, subdir: str = "documents") -> str:
    path = Path(UPLOADS_DIR) / subdir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(file_bytes)
    return str(path)
