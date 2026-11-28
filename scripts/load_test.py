"""Симуляция нагрузки на ML-сервис"""
import argparse
import copy
import json
import random
import time
from pathlib import Path

import requests

DEFAULT_URL = "http://127.0.0.1:8000"
DEFAULT_PAYLOAD = Path(__file__).resolve().parent.parent / "examples" / "predict_request.json"


def make_valid(base: dict, i: int) -> dict:
    """Валидный запрос"""
    payload = copy.deepcopy(base)
    f = payload["features"]
    payload["user_id"] = f"load_user_{i}"
    f["total_area"] = round(random.uniform(20, 150), 1)
    f["living_area"] = round(f["total_area"] * random.uniform(0.4, 0.7), 1)
    f["kitchen_area"] = round(f["total_area"] * random.uniform(0.1, 0.25), 1)
    f["rooms"] = random.randint(1, 5)
    f["floors_total"] = random.randint(5, 25)
    f["floor"] = random.randint(1, f["floors_total"])
    f["build_year"] = random.randint(1960, 2023)
    f["latitude"] = round(random.uniform(55.55, 55.95), 5)
    f["longitude"] = round(random.uniform(37.35, 37.85), 5)
    return payload


def make_invalid(base: dict, i: int) -> dict:
    """Невалидный запрос"""
    payload = copy.deepcopy(base)
    kind = random.choice(["no_features", "bad_type", "missing_field"])
    if kind == "no_features":
        payload.pop("features")
    elif kind == "bad_type":
        payload["features"]["total_area"] = "много"
    else:
        payload["features"].pop("rooms", None)
    return payload


def main() -> None:
    p = argparse.ArgumentParser(description="Нагрузочный скрипт для ML-сервиса")
    p.add_argument("--url", default=DEFAULT_URL, help="адрес сервиса")
    p.add_argument("--requests", type=int, default=200, help="число запросов")
    p.add_argument("--delay", type=float, default=0.2, help="средняя пауза, с")
    p.add_argument("--invalid-share", type=float, default=0.15, help="доля невалидных запросов")
    p.add_argument("--payload", default=str(DEFAULT_PAYLOAD), help="пример запроса")
    args = p.parse_args()

    base = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    stats = {"ok": 0, "client_error": 0, "server_error": 0, "failed": 0}
    latencies = []

    for i in range(1, args.requests + 1):
        invalid = random.random() < args.invalid_share
        payload = make_invalid(base, i) if invalid else make_valid(base, i)
        start = time.perf_counter()
        try:
            r = requests.post(f"{args.url}/predict", json=payload, timeout=10)
            latencies.append(time.perf_counter() - start)
            if r.status_code < 300:
                stats["ok"] += 1
            elif r.status_code < 500:
                stats["client_error"] += 1
            else:
                stats["server_error"] += 1
        except requests.RequestException as exc:
            stats["failed"] += 1
            print(f"[{i}] ошибка соединения: {exc}")
        if i % 25 == 0:
            print(f"отправлено {i}/{args.requests}: {stats}")
        time.sleep(random.expovariate(1 / args.delay) if args.delay > 0 else 0)

    if latencies:
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95) - 1]
        print(f"средняя задержка {sum(latencies)/len(latencies)*1000:.0f} мс, p95 {p95*1000:.0f} мс")
    print("итого:", stats)


if __name__ == "__main__":
    main()