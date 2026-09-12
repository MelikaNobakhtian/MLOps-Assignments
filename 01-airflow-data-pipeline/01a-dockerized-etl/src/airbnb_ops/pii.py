import hashlib
import pandas as pd

# Columns to drop outright
DIRECT_PII_COLUMNS = ["host_name"]

def pseudonymize_value(value, salt: str = "qbc12") -> str:
    """Hash a value with a salt using SHA-256 for stable pseudonymization."""
    raw = f"{salt}:{value}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def handle_pii(df: pd.DataFrame) -> pd.DataFrame:
    """Drop PII columns and pseudonymize host_id -> host_key."""
    df = df.copy()
    
    # Drop direct PII columns that exist
    cols_to_drop = [c for c in DIRECT_PII_COLUMNS if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    
    # Pseudonymize host_id into host_key, then drop host_id
    if "host_id" in df.columns:
        df["host_key"] = df["host_id"].apply(pseudonymize_value)
        df = df.drop(columns=["host_id"])
    
    return df