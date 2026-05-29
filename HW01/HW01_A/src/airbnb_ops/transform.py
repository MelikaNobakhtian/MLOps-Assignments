import pandas as pd

REQUIRED_INPUT_COLUMNS = {
    "listing_id", "neighbourhood", "price", "minimum_nights",
    "availability_365", "number_of_reviews"
}

def build_neighbourhood_summary(listings: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:
    """Aggregate listings by neighbourhood and join segment metadata."""
    # Validate required columns
    missing = REQUIRED_INPUT_COLUMNS - set(listings.columns)
    if missing:
        raise ValueError(f"Missing required columns in listings: {missing}")

    # Aggregate by neighbourhood
    summary = listings.groupby("neighbourhood").agg(
        num_listings=("listing_id", "count"),
        avg_price=("price", "mean"),
        median_price=("price", "median"),
        avg_minimum_nights=("minimum_nights", "mean"),
        availability_365_avg=("availability_365", "mean"),
        total_reviews=("number_of_reviews", "sum"),
    ).reset_index()

    # Derived metric
    summary["reviews_per_listing"] = summary["total_reviews"] / summary["num_listings"]

    # Left join segments so neighbourhoods without a segment get NaN → "unknown"
    summary = summary.merge(segments[["neighbourhood", "tourism_segment", "priority_level"]],
                            on="neighbourhood", how="left")
    summary["tourism_segment"] = summary["tourism_segment"].fillna("unknown")
    summary["priority_level"] = summary["priority_level"].fillna("unknown")

    return summary