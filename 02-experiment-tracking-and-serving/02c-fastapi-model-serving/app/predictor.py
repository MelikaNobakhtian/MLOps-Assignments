from __future__ import annotations

from typing import Iterable, List

import pandas as pd
from fastapi import HTTPException, status

from . import config
from .schemas import ListingFeatures, PredictionResponse


def records_to_dataframe(records: Iterable[ListingFeatures]) -> pd.DataFrame:
    """Convert validated API payloads into the exact DataFrame expected by the model."""
    rows = [record.model_dump() for record in records]
    df = pd.DataFrame(rows)

    # TODO 1: reject unknown fields and forbidden leakage fields.
    # TODO 2: check missing fields against config.EXPECTED_FEATURE_COLUMNS.
    # TODO 3: return df[config.EXPECTED_FEATURE_COLUMNS].
    
    # 1: reject forbidden leakage fields if somehow present
    forbidden_present = [c for c in config.FORBIDDEN_FIELDS if c in df.columns]
    if forbidden_present:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Request contains forbidden leakage or audit fields.",
                "forbidden_fields": forbidden_present,
            },
        )

    # 2: check for missing expected feature columns
    missing_cols = [c for c in config.EXPECTED_FEATURE_COLUMNS if c not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Request is missing required feature fields.",
                "missing_fields": missing_cols,
            },
        )
    # return df with exactly the expected columns in the right order
    return df[config.EXPECTED_FEATURE_COLUMNS]


def predict_records(model, records: List[ListingFeatures]) -> List[PredictionResponse]:
    """TODO: Run model prediction and return API responses."""
    X = records_to_dataframe(records)
    print(X)

    # TODO:
    # - if model has predict_proba, use positive-class probability.
    # - apply config.PREDICTION_THRESHOLD.
    # - return one PredictionResponse per record.
    # Temporary placeholder so the endpoint shape is clear:

    # Get probability scores if available, otherwise fall back to hard predictions
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X)[:, 1]
    else:
        y_score = model.predict(X).astype(float)

    # Apply threshold
    threshold = config.PREDICTION_THRESHOLD
    y_pred = (y_score >= threshold).astype(int)

    # Build one PredictionResponse per record
    responses = []
    for pred, prob in zip(y_pred, y_score):
        responses.append(
            PredictionResponse(
                prediction=int(pred),
                prediction_label=(
                    config.POSITIVE_LABEL if pred == 1 else config.NEGATIVE_LABEL
                ),
                probability=round(float(prob), 6),
                threshold=threshold,
            )
        )

    return responses
