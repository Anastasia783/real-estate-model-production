"""Входные данные"""

from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class ApartmentFeatures(BaseModel):
    """Первичные признаки квартиры"""

    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
    )

    floor: int = Field(strict=True, ge=1)
    rooms: int = Field(strict=True, ge=0)
    build_year: int = Field(strict=True, ge=1)
    building_type_int: int = Field(strict=True, ge=0)
    flats_count: int = Field(strict=True, ge=0)
    floors_total: int = Field(strict=True, ge=1)

    kitchen_area: float | None = Field(default=None, ge=0)
    living_area: float | None = Field(default=None, ge=0)
    total_area: float = Field(gt=0)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    ceiling_height: float | None = Field(default=None, gt=0)

    is_apartment: bool = Field(strict=True)
    studio: bool = Field(strict=True)
    has_elevator: bool = Field(strict=True)
    area_sum_conflict: int = Field(strict=True, ge=0, le=1)

    @model_validator(mode="after")
    def validate_floor(self):
        if self.floor > self.floors_total:
            raise ValueError(
                "floor must not exceed floors_total"
            )
        return self


class PredictionRequest(BaseModel):
    """Запрос на оценку"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "user_id": "test_user",
                    "features": {
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
                    },
                }
            ]
        },
    )

    user_id: (
        Annotated[str, Field(strict=True, min_length=1)]
        | Annotated[int, Field(strict=True, ge=0)]
    )
    features: ApartmentFeatures


class PredictionResponse(BaseModel):
    """Оценка цены"""

    model_config = ConfigDict(allow_inf_nan=False)

    user_id: str | int
    prediction: float