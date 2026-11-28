"""Prometheus метрики"""

from prometheus_client import Counter, Gauge, Histogram


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed",
)

PREDICTION_VALUE_RUB = Histogram(
    "model_prediction_value_rub",
    "Predicted apartment price in rubles",
    buckets=(
        1_000_000, 2_500_000, 5_000_000, 7_500_000, 10_000_000,
        15_000_000, 20_000_000, 30_000_000, 50_000_000, 100_000_000,
    ),
)

INPUT_TOTAL_AREA_M2 = Histogram(
    "model_input_total_area_m2",
    "Total area from prediction requests, square meters",
    buckets=(20, 30, 40, 50, 60, 80, 100, 150, 200, 300),
)

PREDICTION_ERRORS_TOTAL = Counter(
    "model_prediction_errors_total",
    "Internal errors during prediction",
)