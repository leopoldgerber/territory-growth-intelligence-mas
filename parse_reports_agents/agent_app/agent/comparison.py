from pathlib import Path

import pandas as pd


def compare_excel(left_path: Path, right_path: Path) -> dict[str, object]:
    """Compare Excel files.
    Args:
        left_path (Path): Left Excel file.
        right_path (Path): Right Excel file."""
    left_data = pd.read_excel(left_path)
    right_data = pd.read_excel(right_path)
    report = {
        'left_path': str(left_path),
        'right_path': str(right_path),
        'left_rows': len(left_data),
        'right_rows': len(right_data),
        'left_columns': left_data.columns.tolist(),
        'right_columns': right_data.columns.tolist(),
        'columns_match': left_data.columns.tolist() == right_data.columns.tolist(),
    }
    return report
