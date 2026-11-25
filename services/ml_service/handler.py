"""Загрузка модели"""

from pathlib import Path
from threading import Lock

import cloudpickle
import numpy as np
import pandas as pd

from .schemas import PredictionRequest, PredictionResponse


FEATURE_COLUMNS = [
    "floor",
    "rooms",
    "build_year",
    "building_type_int",
    "flats_count",
    "floors_total",
    "kitchen_area",
    "living_area",
    "total_area",
    "latitude",
    "longitude",
    "ceiling_height",
    "is_apartment",
    "studio",
    "has_elevator",
    "area_sum_conflict",
]

NULLABLE_COLUMNS = [
    "kitchen_area",
    "living_area",
    "ceiling_height",
]


class ModelHandler:
    """"""

    def __init__(self, model_path: Path):
        if not model_path.is_file():
            raise FileNotFoundError(
                f"Model file not found: {model_path}"
            )

        # Загружаем только собственный доверенный артефакт.
        with model_path.open("rb") as file:
            self.model = cloudpickle.load(file)

        if not callable(getattr(self.model, "predict", None)):
            raise TypeError("Loaded object has no predict method")
    
        self._predict_lock = Lock()

    def predict(
        self,
        payload: PredictionRequest | dict,
    ) -> PredictionResponse:
        request = PredictionRequest.model_validate(payload)

        frame = pd.DataFrame(
            [request.features.model_dump()],
            columns=FEATURE_COLUMNS,
        )

        for column in NULLABLE_COLUMNS:
            frame[column] = frame[column].astype(float)

        with self._predict_lock:
            predictions = np.asarray(
                self.model.predict(frame),
                dtype=float,
            ).reshape(-1)

        if predictions.size != 1:
            raise RuntimeError(
                "Model must return exactly one prediction"
            )

        if not np.isfinite(predictions).all():
            raise RuntimeError(
                "Model returned a non-finite prediction"
            )

        return PredictionResponse(
            user_id=request.user_id,
            prediction=float(predictions[0]),
        )