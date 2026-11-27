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


В Windows:

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

Windows PowerShell:

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

## Этап 3. Запуск сервисов для системы мониторинга

Инструкция будет добавлена после проверки Docker Compose.

## Этап 4. Построение дашборда для мониторинга

Инструкция будет добавлена после реализации метрик, скрипта нагрузки и дашборда.
