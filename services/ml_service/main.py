"""FastAPI-сервис"""

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .handler import ModelHandler
from .metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
    INPUT_TOTAL_AREA_M2,
    PREDICTION_ERRORS_TOTAL,
    PREDICTION_VALUE_RUB,
)
from .schemas import PredictionRequest, PredictionResponse


logger = logging.getLogger(__name__)

SERVICES_DIR = Path(__file__).resolve().parents[1]


def get_model_path() -> Path:
    configured_path = os.getenv("MODEL_PATH")

    if configured_path:
        path = Path(configured_path)
        if not path.is_absolute():
            path = SERVICES_DIR / path
        return path

    return SERVICES_DIR / "models" / "model.pkl"


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = get_model_path()
    logger.info("Loading model from %s", model_path)

    app.state.handler = ModelHandler(model_path)

    logger.info("Model loaded successfully")
    yield

    app.state.handler = None


app = FastAPI(
    title="Real Estate Price Prediction API",
    description="Оценка стоимости квартиры в рублях.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    method = request.method
    status = "500"
    started = time.perf_counter()
    HTTP_REQUESTS_IN_PROGRESS.inc()

    try:
        response = await call_next(request)
        status = str(response.status_code)
        return response
    finally:
        duration = time.perf_counter() - started
        route = request.scope.get("route")
        path = getattr(route, "path", "unmatched")

        HTTP_REQUESTS_IN_PROGRESS.dec()
        HTTP_REQUESTS_TOTAL.labels(method, path, status).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method, path).observe(duration)


@app.get("/health", tags=["Service"])
def health():
    return {"status": "ok"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Prediction"],
)
def predict(
    payload: PredictionRequest,
    request: Request,
) -> PredictionResponse:
    try:
        result = request.app.state.handler.predict(payload)
    except Exception:
        PREDICTION_ERRORS_TOTAL.inc()
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Prediction failed due to an internal service error",
        ) from None

    INPUT_TOTAL_AREA_M2.observe(payload.features.total_area)
    PREDICTION_VALUE_RUB.observe(result.prediction)
    return result