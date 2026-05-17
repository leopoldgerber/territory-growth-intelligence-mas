from pathlib import Path


def collect_import_files(config: dict[str, object] | None) -> list[Path]:
    """Collect import files.
    Args:
        config (dict[str, object] | None): Schedule config."""
    settings = config or {}
    folder_value = settings.get('import_folder') or settings.get('folder_path')
    if folder_value is None:
        return []
    folder_path = Path(str(folder_value))
    if not folder_path.exists() or not folder_path.is_dir():
        return []
    files = sorted([path for path in folder_path.iterdir() if path.suffix.lower() in ['.xlsx', '.zip']])
    return files
