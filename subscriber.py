import json
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from clickhouse_connect import get_client

# Параметры соединения с RabbitMQ
RABBIT_URL = "amqp://guest:guest@127.0.0.1:5672/"
broker = RabbitBroker(url=RABBIT_URL)
app = FastStream(broker)

# Параметры соединения с ClickHouse
CLICKHOUSE_HOST = "127.0.0.1"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = ""
CLICKHOUSE_DB = "mydb"

ch_client = get_client(
    host=CLICKHOUSE_HOST,
    port=CLICKHOUSE_PORT,
    username=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD,
    database=CLICKHOUSE_DB
)

@broker.subscriber(RabbitQueue(name="data_queue", durable=True))
async def process_message(msg_str: str):
    """
    Получает сообщение в формате JSON-строки,
    парсит его и вставляет запись в таблицу mydb.records
    (id, message, created_at).
    """
    try:
        data = json.loads(msg_str)
        # Генерируем случайный id, либо используем любой другой способ идентификации
        from random import randint
        record_id = randint(1, 10**9)

        # Простейшая вставка (id, message) — столбцы в таблице
        ch_client.command(
            "INSERT INTO mydb.records (id, message) VALUES",
            [(record_id, f"Text: {data['text']}, Value: {data['value']}")]
        )

        print(f"[x] Saved record_id={record_id} to ClickHouse")

    except Exception as e:
        print("[!] Error processing message:", e)
