# Write your predictor functions here
import pandas as pd
from .schema import ListingFeatures, PredictionResponse

def predict_single(features: ListingFeatures, model, run_id: str) -> PredictionResponse:
    df = pd.DataFrame([features.model_dump()])
    pred = int(model.predict(df)[0])
    proba = float(model.predict_proba(df)[0][1])
    return PredictionResponse(prediction=pred, probability_high_demand=proba, model_run_id=run_id)

def predict_batch(features_list: list[ListingFeatures], model, run_id: str) -> list[PredictionResponse]:
    df = pd.DataFrame([f.model_dump() for f in features_list])
    preds = model.predict(df)
    probas = model.predict_proba(df)[:, 1]
    return [
        PredictionResponse(prediction=int(p), probability_high_demand=float(pr), model_run_id=run_id)
        for p, pr in zip(preds, probas)
    ]
