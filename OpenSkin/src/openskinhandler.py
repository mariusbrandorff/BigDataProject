import json
import asyncio
import logging
import threading

from kafka import KafkaConsumer, KafkaProducer
from kafka.consumer.fetcher import ConsumerRecord
from signalrcore.aio.aio_hub_connection_builder import (
    AIOBaseHubConnection,
    AIOHubConnectionBuilder,
)

class OpenSkinHandler:

    conn: AIOBaseHubConnection
    conn_open: bool = False
    kafka_thread: threading.Thread | None = None # Should be in the constructor?
    symbols: set[str] = set() # Should be in the constructor? Probably not.

    # Env
    in_topic: str
    out_topic: str
    bootstrap_servers: str

    def __init__(self, in_topic: str, out_topic: str, bootstrap_servers: str, hub_url: str):
        self.conn = (
            AIOHubConnectionBuilder()
            .with_url(hub_url)
            .configure_logging(logging.DEBUG)
            .build()
        )

        self.conn.on_open(self.on_open)
        self.conn.on_close(self.on_close)
        self.conn.on_error(lambda data: self.on_error(data.error))

        self.in_topic = in_topic
        self.out_topic = out_topic
        self.bootstrap_servers = bootstrap_servers

        self._producer: KafkaProducer | None = None
    
    @property
    def kafka_consumer(self) -> KafkaConsumer:
        return KafkaConsumer(
            self.in_topic,
            bootstrap_servers=self.bootstrap_servers
        )

    @property
    def kafka_producer(self) -> KafkaProducer:
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers
            )
        return self._producer

    def kafka_listen(self):
        msg: ConsumerRecord
        consumer = self.kafka_consumer
        for msg in consumer:
            if not isinstance(msg, ConsumerRecord):
                print("Something wrong!?")
                raise Exception(
                    "Message from kafka wasn't the expected type: ConsumerRecord"
                )

            symbol: str | None = None
            if isinstance(msg.value, bytes):
                symbol = msg.value.decode("utf-8")  # Correct format or not?

            if symbol is not None:
                threading.Thread(
                    None, asyncio.run(self.new_symbol(symbol)), daemon=True
                ).start()

    async def new_symbol(self, symbol: str) -> None:
        """Append the new symbol to existing subscription list
        and subscribe through biquote websocket"""

        if symbol in self.symbols:
            print("Symbol ", symbol, " exists")
            return

        self.symbols.add(symbol)
        print("New symbols:", self.symbols)
        if self.conn_open:
            symbols = [symbol]
            await self.conn.invoke("Subscribe", [symbols])
        else:
            logging.warning(
                "Symbol added whilst connection not open, not invoking subscribe"
            )


    async def start(self):
        await self.conn.start()

        # TODO: Load all already tracked symbols

        self.kafka_thread = threading.Thread(None, self.kafka_listen, daemon=True)
        self.kafka_thread.start()

    def on_open(self):
        self.conn_open = True

    def on_close(self):
        self.conn_open = False

    def on_error(self, error: Exception):
        self.conn_open = False
        raise error

    @property
    def is_running(self):
        if (
            self.conn_open
            and self.kafka_thread is not None
            and self.kafka_thread.is_alive()
        ):
            return True
        return False


""" For testing of kafka. """
#"""
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    handler = OpenSkinHandler(
        in_topic="symbols",
        out_topic="test",
        bootstrap_servers="localhost:9092",
        hub_url="https://biquote.io/hubs/tick", # Just needed an actual url for testing
    )

    try:
        asyncio.run(handler.start())
    except KeyboardInterrupt:
        pass
#"""