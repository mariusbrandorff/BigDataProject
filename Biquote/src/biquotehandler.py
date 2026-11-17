import asyncio
from datetime import datetime
import io
import logging
import threading

import avro
import avro.schema
import avro.io
from kafka import KafkaConsumer, KafkaProducer
from kafka.consumer.fetcher import ConsumerRecord
from signalrcore.aio.aio_hub_connection_builder import (
    AIOBaseHubConnection,
    AIOHubConnectionBuilder,
)

from models import json_to_tick, to_avro_tick


class BiquoteHandler:

    conn: AIOBaseHubConnection
    conn_open: bool = False
    kafka_thread: threading.Thread | None
    symbols: set[str] = set()

    # Env
    in_topic: str
    out_topic: str
    bootstrap_servers: str

    """docstring for BiquoteHandler."""

    def __init__(self, in_topic: str, out_topic: str, bootstrap_servers: str):
        self.conn = (
            AIOHubConnectionBuilder()
            .with_url("https://biquote.io/hubs/tick")
            .configure_logging(logging.DEBUG)
            .build()
        )

        self.conn.on_open(self.on_open)
        self.conn.on_close(self.on_close)
        self.conn.on_error(lambda data: self.on_error(data.error))
        self.conn.on("ReceiveTick", self.receive_tick)

        self.in_topic = in_topic
        self.out_topic = out_topic
        self.bootstrap_servers = bootstrap_servers

    # Init extras
    ## Kafka
    @property
    def kafka_consumer(self) -> KafkaConsumer:
        return KafkaConsumer(self.in_topic, bootstrap_servers=self.bootstrap_servers)

    _kafka_producer: KafkaProducer | None = None

    @property
    def kafka_producer(self) -> KafkaProducer:
        if self._kafka_producer is None:
            self._kafka_producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers
            )
        return self._kafka_producer

    ## Avro

    _schema: avro.schema.Schema | None = None
    _schema_time: datetime  # Maybe not needed

    @property
    def schema(self) -> avro.schema.Schema:
        """Returns the avro schema. If any changes have been made since last return, it loads the new schema."""
        if self._schema is None:
            self._schema = avro.schema.parse(open("schema.avsc").read())
        return self._schema

    # Properties
    @property
    def is_running(self):
        if (
            self.conn_open
            and self.kafka_thread is not None
            and self.kafka_thread.is_alive()
        ):
            return True
        return False

    # Public methods
    async def start(self):
        await self.conn.start()

        # TODO: Load all already tracked symbols

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

    def receive_tick(self, k: list):
        ticks = [json_to_tick(t) for t in k]

        for (
            tick
        ) in (
            ticks
        ):  # For every tick (despite that fact that we have yet to observe multiple ticks in one response)
            writer = avro.io.DatumWriter(self.schema)
            bytes_writer = io.BytesIO()
            encoder = avro.io.BinaryEncoder(bytes_writer)
            writer.write(to_avro_tick(tick), encoder)
            raw_bytes = bytes_writer.getvalue()
            self.kafka_producer.send(self.out_topic, raw_bytes)

    # Kafka
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
        self.symbols.add(symbol)
        print("New symbols:", self.symbols)
        if self.conn_open:
            symbols = [symbol]
            await self.conn.invoke("Subscribe", [symbols])
        else:
            logging.warning(
                "Symbol added whilst connection not open, not invoking subscribe"
            )
