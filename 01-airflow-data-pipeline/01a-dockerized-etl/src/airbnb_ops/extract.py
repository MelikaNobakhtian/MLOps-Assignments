from pathlib import Path
import pandas as pd

def read_csv_checked(path: Path) -> pd.DataFrame:
    """Read a CSV file, raising FileNotFoundError if it doesn't exist."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")
    return pd.read_csv(path)