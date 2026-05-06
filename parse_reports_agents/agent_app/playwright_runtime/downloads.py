import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class DownloadRecord:
    domain: str
    report_name: str
    month_name: str
    file_path: str


def manifest_path(downloads_path: Path) -> Path:
    """Build manifest path.
    Args:
        downloads_path (Path): Downloads directory."""
    path = downloads_path / 'download_manifest.json'
    return path


def read_manifest(downloads_path: Path) -> list[dict[str, str]]:
    """Read download manifest.
    Args:
        downloads_path (Path): Downloads directory."""
    path = manifest_path(downloads_path)
    if not path.exists():
        return []
    records = json.loads(path.read_text(encoding='utf-8'))
    return records


def write_manifest(downloads_path: Path, records: list[dict[str, str]]) -> Path:
    """Write download manifest.
    Args:
        downloads_path (Path): Downloads directory.
        records (list[dict[str, str]]): Manifest records."""
    downloads_path.mkdir(parents=True, exist_ok=True)
    path = manifest_path(downloads_path)
    path.write_text(json.dumps(records, indent=2), encoding='utf-8')
    return path


def add_download(downloads_path: Path, record: DownloadRecord) -> Path:
    """Add download record.
    Args:
        downloads_path (Path): Downloads directory.
        record (DownloadRecord): Download record."""
    records = read_manifest(downloads_path)
    records.append(asdict(record))
    path = write_manifest(downloads_path, records)
    return path
