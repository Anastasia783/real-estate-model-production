# Инструкция по запуску

Все команды выполняются из корня репозитория

## Этап 1. Написание FastAPI-микросервиса

### Требования:
Python 3.11
Git
Доступ к интернету для установки Python-зависимостей

Берем обученную модель из прошлого проекта. которая находится в `services/models/model.pkl`.Модель перенесена в новый проект, поэтому доступ к старому проекту  для запуска не требуется.

### Получение проекта
git clone [https://github.com/Anastasia783/real-estate-model-production.git](https://github.com/Anastasia783/real-estate-model-production.git)
cd real-estate-model-production


### Создание окружения и установка зависимостей

PowerShell:
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt


### Проверка модели без API
python scripts/check_model.py


.\.venv\Scripts\python.exe scripts/check_model.py


Скрипт загружает модель, получает предсказание для тестовой квартиры и сравнивает его с результатом исходного окружения.

Ожидаемое предсказание: около 18 709 403,43 руб.При успешной проверке выводится сообщение `SUCCESS`.

### Запуск API
python -m uvicorn services.ml_service.main:app --host 127.0.0.1 --port 8000


В Windows:
.\.venv\Scripts\python.exe -m uvicorn services.ml_service.main:app --host 127.0.0.1 --port 8000

Модель загружается один раз при старте приложения.

Адреса:
Swagger UI: http://127.0.0.1:8000/docs
Получение предсказания: POST http://127.0.0.1:8000/predict

### Проверка состояния
Запросы выполняются во втором терминале, пока сервер работает.

curl.exe http://127.0.0.1:8000/health

Ожидаем:

{"status": "ok"}


### Пример запроса на предсказание
Готовый запрос находится в `examples/predict_request.json`

curl.exe -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" --data-binary "@examples/predict_request.json"


Ожидаем:

{
  "user_id": "test_user",
  "prediction": 18709403.429664556
}


 Параметр `prediction` — оценка стоимости квартиры в рублях

### Проверка валидации

Откройте Swagger UI, выберите POST /predict и нажмите Try it out. 

1. нужно выполнить подготовленный пример, ожидается HTTP 200
2. А теперь заменим`total_area` на `-55` и повторим запрос: ожидаем HTTP 422.
- В описании ошибки должно быть указано поле: body - features - total_area и требование значения больше нуля.

Дополнительные проверки схемы включают обязательные поля, типы данных, запрет лишних полей и условие `floor <= floors_total`.
Поля kitchen_area, living_area, ceiling_height могут принимать `null`: пропуски обрабатываются обученным
пайплайном модели.

### Настройка расположения модели

По умолчанию используется `services/models/model.pkl`. 

Путь можно переопределить переменной окружения `MODEL_PATH`. Относительный путь разрешается от директории services,абсолютный используется без изменений. 

Для стандартного локального запуска переменные окружения и файл .env не требуются.

## Этап 2. Запуск в Docker

### Требования
Команда `docker version` показывает `Client` и `Server`


### Сборка 
docker build -f Dockerfile_ml_service -t real-estate-ml-service:local 


### Запуск контейнера
docker run -d --name real-estate-ml-service -p 127.0.0.1:8001:8000 real-estate-ml-service:local

Сервис доступен на `http://127.0.0.1:8001`, он слушает порт 8000.

### Проверка
docker ps
docker logs --tail 50 real-estate-ml-service

curl.exe -i "http://127.0.0.1:8001/health"

curl.exe -i -X POST "http://127.0.0.1:8001/predict" -H "Content-Type: application/json" --data-binary "@examples/predict_request.json"

По итогам проверки ожидаем:
статус контейнера `Up ... (healthy)`
/health возвращает HTTP 200 и `{"status":"ok"}`;
/predict возвращает HTTP 200, user_id равный `test_user`, а `prediction` около 18709403.43

### Остановка 
docker stop real-estate-ml-service
docker rm real-estate-ml-service

## Этап 3. Запуск через Docker Compose

### Требования
Команда `docker` доступна в терминале. Настройки находятся в `services/.env`
Локальный сервер из этапа 1 остановлен (Ctrl+C), иначе порт 8000 занят.

### Запуск
docker compose --env-file services/.env up -d --build


### Проверка
docker compose --env-file services/.env ps
curl.exe -i "http://127.0.0.1:8000/health"

curl.exe -i -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" --data-binary "@examples/predict_request.json"

Ожидаем: 
ml_service имеет статус `healthy`
/health возвращает HTTP 200 и `{"status":"ok"}`
/predict возвращает HTTP 200, user_id равен test_user`, а prediction примерно 18709403.43.

### Логи
docker compose --env-file services/.env logs --tail 50 ml_service


### Остановка
docker compose --env-file services/.env down


## Этап 4. Построение дашборда для мониторинга:Prometheus и Grafana

### В составе:
services/prometheus/prometheus.yml — конфиг Prometheus (каждые 15 с)
services/grafana/provisioning/datasources/prometheus.yml — datasource Prometheus (`uid: prometheus`, `url: http://prometheus:9090`).
services/grafana/provisioning/dashboards/dashboards.yml — провайдер дашбордов (путь: /etc/grafana/dashboards)
services/grafana/dashboards/real-estate-ml-service.json — дашборд Real Estate ML Service

### Запуск
docker compose up -d

Grafana: http://127.0.0.1:3000 (логин и пароль:  admin/admin)
Дашборд: http://127.0.0.1:3000/d/real-estate-ml-service

### Проверка
curl.exe -s "http://127.0.0.1:9090/api/v1/targets"

curl.exe -s -u admin:admin "http://127.0.0.1:3000/api/datasources"

curl.exe -s -u admin:admin "http://127.0.0.1:3000/api/search?query=Real"

Ожидаем:ml_service:8000 - `up`.

### Нагрузка
1..30 | ForEach-Object { curl.exe -s -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" --data-binary "@examples/predict_request.json" | Out-Null; Start-Sleep -Milliseconds 300 }

### Что показывает дашборд
1.Запросы в секунду
2.Задержка p95, с
3.Средний прогноз в руб.
4.Средняя площадь в квадратных метрах
5.Ошибки модели за час

После нагрузки на графиках появляются данные, Ошибки модели за час должны быть равны 0

### Остановка
docker compose stop grafana
docker compose down


### Пересоздание Grafana
Если datasource или дашборд не обновились после правки файлов:

docker compose stop grafana
docker compose rm -f grafana
docker volume rm real-estate-model-production_grafana_data
docker compose up -d grafana

Данные Grafana (пароли, ручные правки) будут удалены.

### Проблематика
Может быть ошибка Datasource not found — это значит, что  открыта старая вкладка со старым uid. Нужно открыть страницу  в инкогнито.
Если панели пустые — отправь запросы на `/predict` и подожди 15–30 с.

