# RabbitMQ + ClickHouse + FastAPI
Проект обработки данных:
- **FastAPI** для HTTP-эндпоинтов;
- **RabbitMQ** для брокера сообщений;
- **FastStream** (обёртка над RabbitMQ) для упрощения подписки и публикации;
- **ClickHouse** для хранения и аналитики.

## Запуск проекта

1. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

2. Запустите контейнер с RabbitMQ (через Docker Compose):
    ```bash
    docker-compose up -d
    ```

3. Запустите ClickHouse локально или в Docker-контейнере:
    ```bash
    docker run -d \
        --name some-clickhouse-server \
        -p 8123:8123 -p 9000:9000 -p 9009:9009 \
        --ulimit nofile=262144:262144 \
        clickhouse/clickhouse-server
    ```

4. Создайте таблицу в ClickHouse (при необходимости):
    ```sql
    CREATE DATABASE IF NOT EXISTS mydb;
    CREATE TABLE IF NOT EXISTS mydb.records (
        id UInt64,
        message String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY id;
    ```

5. Запустите **FastAPI**:
    ```bash
    python main.py
    ```
    или
    ```bash
    uvicorn main:app --reload
    ```

6. Запустите **подписчика**:
    ```bash
    faststream run subscriber:app
    ```

7. Проверьте работу:
    ```bash
    # POST /send
    curl -X POST -H "Content-Type: application/json" \
         -d '{"text":"Hello from Rabbit", "value":42}' \
         http://127.0.0.1:8000/send

    # GET /data
    curl http://127.0.0.1:8000/data
    ```

