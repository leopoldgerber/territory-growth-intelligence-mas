from pathlib import Path

import pandas as pd

from agent_app.agent.action_result import ActionResult, failure_result, success_result


def validate_file(file_path: Path) -> ActionResult:
    """Validate file exists.
    Args:
        file_path (Path): File path."""
    if not file_path.exists():
        return failure_result('File validation failed', f'File not found: {file_path}', {'path': str(file_path)})
    if file_path.stat().st_size == 0:
        return failure_result('File validation failed', f'File is empty: {file_path}', {'path': str(file_path)})
    return success_result('File validated', {'path': str(file_path)})


def validate_csv(file_path: Path, required_columns: list[str] | None = None) -> ActionResult:
    """Validate CSV file.
    Args:
        file_path (Path): CSV file path.
        required_columns (list[str] | None): Required columns."""
    file_result = validate_file(file_path)
    if not file_result.success:
        return file_result
    try:
        data = pd.read_csv(file_path)
    except Exception as error:
        return failure_result('CSV validation failed', str(error), {'path': str(file_path)})
    if required_columns is not None:
        missing_columns = [column_name for column_name in required_columns if column_name not in data.columns]
        if len(missing_columns) > 0:
            return failure_result('CSV columns missing', ', '.join(missing_columns), {'path': str(file_path)})
    return success_result('CSV validated', {'path': str(file_path), 'rows': len(data)})


def validate_excel(file_path: Path) -> ActionResult:
    """Validate Excel file.
    Args:
        file_path (Path): Excel file path."""
    file_result = validate_file(file_path)
    if not file_result.success:
        return file_result
    try:
        data = pd.read_excel(file_path)
    except Exception as error:
        return failure_result('Excel validation failed', str(error), {'path': str(file_path)})
    return success_result('Excel validated', {'path': str(file_path), 'rows': len(data)})
