# Write your FastAPI app here

import os

import mlflow
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager

from .predictor import predict_single, predict_batch
from .schema import ListingFeatures, PredictionResponse

model_store: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_id = os.environ["MODEL_RUN_ID"]
    tracking_uri = os.environ["MLFLOW_TRACKING_URI"]

    os.environ.setdefault("MLFLOW_TRACKING_USERNAME", os.environ.get("MLFLOW_TRACKING_USERNAME", ""))
    os.environ.setdefault("MLFLOW_TRACKING_PASSWORD", os.environ.get("MLFLOW_TRACKING_PASSWORD", ""))

    mlflow.set_tracking_uri(tracking_uri)

    model_store["model"] = mlflow.sklearn.load_model(f"runs:/{run_id}/model")
    model_store["run_id"] = run_id

    yield

    model_store.clear()


app = FastAPI(
    title="Airbnb Listing Demand Prediction API",
    description="HW03 model serving API. See /docs for interactive Swagger UI.",
    lifespan=lifespan,
)


@app.get("/health", tags=["service"])
def health() -> dict:
    if "model" not in model_store:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded",
        )
    return {"status": "ok", "model_run_id": model_store["run_id"]}


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(features: ListingFeatures) -> PredictionResponse:
    if "model" not in model_store:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded",
        )
    return predict_single(features, model_store["model"], model_store["run_id"])


@app.post("/predict/batch", response_model=list[PredictionResponse], tags=["prediction"])
def predict_batch_endpoint(features: list[ListingFeatures]) -> list[PredictionResponse]:
    if "model" not in model_store:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded",
        )
    return predict_batch(features, model_store["model"], model_store["run_id"])
