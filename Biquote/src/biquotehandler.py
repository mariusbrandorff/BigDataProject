from argparse import Namespace
import asyncio
import logging
import threading

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from signalrcore.aio.aio_hub_connection_builder import AIOBaseHubConnection, AIOHubConnectionBuilder

class BiquoteHandler:

    conn: AIOBaseHubConnection
    conn_open: bool = False
    kafka_thread: threading.Thread | None
    symbols: set[str] = set()

    """docstring for BiquoteHandler."""
    def __init__(self, in_topic: str, out_topic: str, bootstrap_servers: str):
        self.conn = AIOHubConnectionBuilder()\
                .with_url("https://biquote.io/hubs/tick")\
                .configure_logging(logging.DEBUG)\
                .build()

        self.conn.on_open(self.on_open)
        self.conn.on_close(self.on_close)
        self.conn.on_error(lambda data: self.on_error(data.error))
        self.conn.on("ReceiveTick", self.receive_tick)

        
        self.in_topic = in_topic
        self.out_topic = out_topic
        self.bootstrap_servers = bootstrap_servers

    # Init extras
    @property
    def kafka_consumer(self):
        return KafkaConsumer(
            self.in_topic,
            bootstrap_servers=self.bootstrap_servers
        )

    # Properties
    @property
    def is_running(self):
        if (self.conn_open and self.kafka_thread is not None and self.kafka_thread.is_alive()):
            return True
        return False

    # Public methods
    async def start(self):
        await self.conn.start()
        self.kafka_thread = threading.Thread(None, self.kafka_listen, daemon=True)
        self.kafka_thread.start()

    # Signal
    def on_open(self):
        self.conn_open = True

    def on_close(self):
        self.conn_open = False

    def on_error(self, error: Exception):
        self.conn_open = False
        raise error

    def receive_tick(self, k):
        print(type(k))

    # Kafka
    def kafka_listen(self):
        msg: ConsumerRecord
        consumer = self.kafka_consumer
        for msg in consumer:
            if not isinstance(msg, ConsumerRecord):
                print("Something wrong!?")
                return
            
            print(msg.topic, msg.partition, msg.offset, msg.value)
            print(type(msg.value))
            symbol: str | None = None
            if (isinstance(msg.value, bytes)):
                symbol = msg.value.decode("utf-8")

            if (symbol is not None):
                threading.Thread(None, asyncio.run(self.new_symbol(symbol)), daemon=True).start()
            
            

    async def new_symbol(self, symbol: str) -> None:
        """Sanitize new symbol, append to existing subscription list 
        and subscribe through biquote websocket"""
        self.symbols.add(symbol)
        print("New symbols:", self.symbols)
        if (self.conn_open):
            symbols = [symbol]
            await self.conn.invoke("Subscribe", [symbols])
        else:
            logging.warning("Symbol added whilst connection not open, not invoking subscribe")