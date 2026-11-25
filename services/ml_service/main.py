"""FastAPI-сервис"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

from .handler import ModelHandler
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


@app.get("/health", tags=["Service"])
def health():
    return {"status": "ok"}


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
        return request.app.state.handler.predict(payload)
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Prediction failed due to an internal service error",
        ) from None