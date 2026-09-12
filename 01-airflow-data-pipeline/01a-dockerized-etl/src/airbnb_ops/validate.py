import pandas as pd

REQUIRED_OUTPUT_COLUMNS = {
    "neighbourhood", "num_listings", "avg_price", "median_price",
    "avg_minimum_nights", "availability_365_avg", "total_reviews",
    "reviews_per_listing", "tourism_segment", "priority_level"
}

PII_COLUMNS = {"host_name", "host_id", "reviewer_name", "reviewer_id",
               "listing_url", "host_url"}

def validate_summary(summary: pd.DataFrame) -> None:
    """Validate the neighbourhood summary dataframe. Raises ValueError on failure."""
    if summary.empty:
        raise ValueError("Output dataframe is empty.")

    missing_cols = REQUIRED_OUTPUT_COLUMNS - set(summary.columns)
    if missing_cols:
        raise ValueError(f"Missing required output columns: {missing_cols}")

    leaked_pii = PII_COLUMNS & set(summary.columns)
    if leaked_pii:
        raise ValueError(f"PII columns found in output: {leaked_pii}")

    if summary["neighbourhood"].isnull().any():
        raise ValueError("Null values found in 'neighbourhood' column.")

    if (summary["num_listings"] <= 0).any():
        raise ValueError("'num_listings' must be > 0 for all rows.")

    if (summary["avg_price"] < 0).any():
        raise ValueError("'avg_price' must be >= 0 for all rows.")

    if not summary["availability_365_avg"].between(0, 365).all():
        raise ValueError("'availability_365_avg' must be between 0 and 365.")