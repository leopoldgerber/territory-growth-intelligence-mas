from pathlib import Path
from zipfile import BadZipFile, ZipFile


def safe_member(member_name: str) -> bool:
    """Check archive member.
    Args:
        member_name (str): Archive member name."""
    member_path = Path(member_name)
    is_safe = not member_path.is_absolute() and '..' not in member_path.parts
    return is_safe


def extract_archive(file_path: Path) -> tuple[list[Path], list[str]]:
    """Extract archive files.
    Args:
        file_path (Path): ZIP file path."""
    extract_path = file_path.with_suffix('')
    extract_path.mkdir(parents=True, exist_ok=True)
    errors = []
    try:
        with ZipFile(file_path) as archive:
            for member_name in archive.namelist():
                if member_name.endswith('/') or '__MACOSX' in member_name:
                    continue
                if safe_member(member_name):
                    archive.extract(member_name, extract_path)
                else:
                    errors.append(f'Skipped unsafe archive member: {member_name}')
    except BadZipFile:
        errors.append('ZIP archive is not readable.')
    excel_paths = [path for path in extract_path.rglob('*.xlsx') if path.is_file()]
    return excel_paths, errors


def collect_excels(file_path: Path) -> tuple[list[Path], list[str]]:
    """Collect Excel files.
    Args:
        file_path (Path): Uploaded file path."""
    if file_path.suffix.lower() == '.zip':
        excel_paths, errors = extract_archive(file_path)
        return excel_paths, errors
    return [file_path], []
