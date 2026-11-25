"""Проверка загрузки"""

import sys
from importlib.metadata import version
from pathlib import Path

import cloudpickle
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "services" / "models" / "model.pkl"
MODULE_DIR = PROJECT_ROOT / "services" / "ml_service"

sys.path.insert(0, str(MODULE_DIR))

REFERENCE_PREDICTION = 18709403.429664556


def main():
    print("Python executable:", sys.executable)
    print("Project root:", PROJECT_ROOT)

    for package in (
        "numpy",
        "pandas",
        "scikit-learn",
        "autofeat",
        "cloudpickle",
    ):
        print(f"{package}: {version(package)}")

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    # Загружаем только собственный, доверенный артефакт модели.
    with MODEL_PATH.open("rb") as file:
        model = cloudpickle.load(file)

    print("\nModel type:", type(model).__name__)
    print("Pipeline steps:", list(model.named_steps))

    sample = pd.DataFrame(
        [
            {
                "floor": 5,
                "rooms": 2,
                "build_year": 2000,
                "building_type_int": 1,
                "flats_count": 100,
                "floors_total": 12,
                "kitchen_area": 10.0,
                "living_area": 30.0,
                "total_area": 55.0,
                "latitude": 55.75,
                "longitude": 37.62,
                "ceiling_height": 2.7,
                "is_apartment": False,
                "studio": False,
                "has_elevator": True,
                "area_sum_conflict": 0,
            }
        ]
    )

    predictions = np.asarray(
        model.predict(sample), dtype=float
    ).reshape(-1)

    if predictions.size != 1:
        raise ValueError(
            f"Expected one prediction, received: {predictions.size}"
        )

    if not np.isfinite(predictions).all():
        raise ValueError(f"Non-finite prediction: {predictions}")

    prediction = float(predictions[0])

    print(f"\nPrediction: {prediction:.8f}")
    print(f"Reference:  {REFERENCE_PREDICTION:.8f}")
    print(
        "Absolute difference:",
        abs(prediction - REFERENCE_PREDICTION),
    )

    np.testing.assert_allclose(
        prediction,
        REFERENCE_PREDICTION,
        rtol=1e-10,
        atol=1e-6,
        err_msg="Prediction differs from the original environment",
    )

    print("\nSUCCESS: model loaded and prediction matches reference.")


if __name__ == "__main__":
    main()