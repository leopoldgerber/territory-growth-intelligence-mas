import hashlib
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


ALLOWED_SUFFIXES = {'.xlsx', '.zip'}


def ensure_storage() -> Path:
    """Ensure upload storage.
    Args:
        None (None): No arguments are required."""
    settings = get_settings()
    storage_path = Path(settings.upload_storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def validate_upload(upload_file: UploadFile) -> str:
    """Validate upload file.
    Args:
        upload_file (UploadFile): Uploaded file."""
    file_name = upload_file.filename or ''
    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        return 'Only .xlsx and .zip files are supported.'
    return ''


def save_upload(upload_file: UploadFile) -> Path:
    """Save uploaded file.
    Args:
        upload_file (UploadFile): Uploaded file."""
    storage_path = ensure_storage()
    file_name = Path(upload_file.filename or 'upload.bin').name
    upload_path = storage_path / f'{uuid4().hex}_{file_name}'
    with upload_path.open('wb') as target_file:
        shutil.copyfileobj(upload_file.file, target_file)
    return upload_path


def file_hash(file_path: Path) -> str:
    """Calculate file hash.
    Args:
        file_path (Path): File path."""
    digest = hashlib.sha256()
    with file_path.open('rb') as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()
