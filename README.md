# Real Estate ML Service

Сервис оценки стоимости квартир. Обученная модель из предыдущего проекта (`services/models/model.pkl`) работает за FastAPI-микросервисом. Сервис упакован в Docker, запускается через Docker Compose, а его метрики собирает Prometheus и показывает Grafana.

## Возможности

POST /predict возвращает оценку стоимости квартиры в рублях.
GET /health  проверяет состояние сервиса.
Валидация входных данных: обязательные поля, типы, запрет лишних полей
Мониторинг: Prometheus собирает метрики с /metrics, а дашборд Grafana Real Estate ML Service создаётся автоматически.

## Cтарт

Нужны Docker и Docker Compose. 
docker compose --env-file services/.env up -d --build


Проверка:
curl.exe -i "http://127.0.0.1:8000/health"
curl.exe -i -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" --data-binary "@examples/predict_request.json"


Ожидаем:
{
  "user_id": "test_user",
  "prediction": 18709403.429664556
}
```

## Адреса

Swagger UI     http://127.0.0.1:8000/docs 
ML-сервис      http://127.0.0.1:8000 
Prometheus     http://127.0.0.1:9090 
Grafana        http://127.0.0.1:3000 (admin/admin) 
Дашборд        http://127.0.0.1:3000/d/real-estate-ml-service 

## Дашборд мониторинга

На дашборде пять панелей: запросы в секунду, задержка p95, средний прогноз в рублях, cредняя площадь в квадратных метрах и ошибки модели за час. Datasource и дашборд подключаются автоматически (provisioning), вручную настраивать ничего не нужно.

Чтобы на графиках появились данные, нужна нагрузка:
1..30 | ForEach-Object { curl.exe -s -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" --data-binary "@examples/predict_request.json" | Out-Null; Start-Sleep -Milliseconds 300 }


## Структура репозитория

Dockerfile_ml_service      образ ML-сервиса
docker-compose.yaml        ml_service, prometheus, grafana
examples/                  пример запроса predict_request.json
scripts/
check_model.py             проверка модели без API
services/
.env                       настройки Compose
ml_service/
 main.py                   FastAPI-приложение
handler.py                 загрузка модели и предсказание
schemas.py                 схемы запросов и валидация
metrics.py                 метрики для Prometheus
enriched_transformer.py
models/
model.pkl
final_model_configuration.json
prometheus/
prometheus.yml
grafana/
dashboards/                 real-estate-ml-service.json
provisioning/               datasources и dashboards
Instructions.md             пошаговая инструкция по этапам
Monitoring.md               описание мониторинга
README.md


## Остановка
docker compose --env-file services/.env down


## Документация

Пошаговая инструкция по этапам (локальный запуск, Docker, Compose, мониторинг) и решение типичных проблем находятся в [Instructions.md](Instructions.md) и в [Monitoring.md](Monitoring.md)

