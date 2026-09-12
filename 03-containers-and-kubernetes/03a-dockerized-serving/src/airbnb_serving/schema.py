# Write your Pydantic schemas here

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ListingFeatures(BaseModel):

    # --- categorical / string features ---
    room_type: str
    property_type: str
    neighbourhood_name: str

    # --- core listing attributes ---
    accommodates: int
    bedrooms: Optional[float] = None
    beds: Optional[float] = None
    bathrooms: Optional[float] = None
    listing_price: Optional[float] = None
    minimum_nights: int
    maximum_nights: int

    # --- booleans ---
    instant_bookable: bool
    is_superhost: bool

    # --- host / review history ---
    host_listing_count: int
    total_reviews_before_cutoff: Optional[float] = None
    unique_reviewers_before_cutoff: Optional[float] = None
    avg_comment_len_before_cutoff: Optional[float] = None
    max_comment_len_before_cutoff: Optional[float] = None
    days_since_last_review: Optional[float] = None

    # --- availability / calendar, last 90 days ---
    available_days_last_90d: int
    available_rate_last_90d: float
    avg_minimum_nights_calendar_last_90d: Optional[float] = None
    avg_maximum_nights_calendar_last_90d: Optional[float] = None

    # --- availability / calendar, last 30 days ---
    available_days_last_30d: int
    available_rate_last_30d: float
    avg_minimum_nights_calendar_last_30d: Optional[float] = None
    avg_maximum_nights_calendar_last_30d: Optional[float] = None


class PredictionResponse(BaseModel):
    """Response for both /predict and /predict/batch (one item per row)."""

    listing_id: Optional[int] = None
    prediction: int
    probability_high_demand: float
    model_run_id: str
