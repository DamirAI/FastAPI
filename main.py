from fastapi import FastAPI
from pydantic import BaseModel
from faststream.rabbit import RabbitBroker
from faststream import FastStream
from clickhouse_connect import get_client

import uvicorn
import json


# ----------------
# 1. Настройки
# ----------------

# Параметры соединения с ClickHouse
CLICKHOUSE_HOST = "127.0.0.1"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = ""
CLICKHOUSE_DB = "mydb"

# Подключаемся к ClickHouse
ch_client = get_client(
    host=CLICKHOUSE_HOST,
    port=CLICKHOUSE_PORT,
    username=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD,
    database=CLICKHOUSE_DB
)

# Параметры соединения с RabbitMQ
RABBIT_URL = "amqp://guest:guest@127.0.0.1:5672/"
broker = RabbitBroker(url=RABBIT_URL)

# Инициализация FastAPI-приложения
app = FastAPI()

# Модель входных данных
class MyData(BaseModel):
    text: str
    value: int


# ----------------
# 2. Роуты / эндпоинты
# ----------------

@app.post("/send")
async def send_data(item: MyData):
    """
    Принимаем JSON-данные от пользователя,
    кладём сообщение в очередь RabbitMQ.
    """
    payload = item.dict()
    message_str = json.dumps(payload)

    # Публикуем сообщение в очередь "data_queue"
    async with broker:
        await broker.publish(message_str, routing_key="data_queue")

    return {
        "status": "Message sent to RabbitMQ",
        "data": payload
    }

@app.get("/data")
def get_data():
    """
    Получаем данные из ClickHouse и возвращаем их как JSON.
    Предположим, что у нас есть таблица mydb.records
    со столбцами (id, message, created_at).
    """
    rows = ch_client.query("SELECT id, message, created_at FROM mydb.records")
    result = []
    for row in rows.result_rows:
        result.append({
            "id": row[0],
            "message": row[1],
            "created_at": str(row[2])
        })
    return {"data": result}


# ----------------
# 3. Точка входа
# ----------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
