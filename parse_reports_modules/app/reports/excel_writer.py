from pathlib import Path

import pandas as pd


def write_excel(data: pd.DataFrame | pd.Series, output_path: Path, sheet_name: str = 'Лист 1') -> Path:
    """Write data to Excel.
    Args:
        data (pd.DataFrame | pd.Series): Data to write.
        output_path (Path): Excel output path.
        sheet_name (str): Excel sheet name."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name=sheet_name, index=False)
    return output_path
