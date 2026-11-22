import threading
import time

from kafka import KafkaConsumer, KafkaProducer
from kafka.consumer.fetcher import ConsumerRecord

from openskin import get_skins
from models import to_avro_skin

import avro
import avro.schema
import avro.io
import io

class OpenSkinHandler:
    
    # Env
    in_topic: str
    out_topic: str
    bootstrap_servers: str

    def __init__(self, in_topic: str, out_topic: str, bootstrap_servers: str):
        self.in_topic = in_topic
        self.out_topic = out_topic
        self.bootstrap_servers = bootstrap_servers

        self.symbols: set[str] = set()

        self.kafka_thread: threading.Thread | None = None
        self.retrieve_thread: threading.Thread | None = None
        self._producer: KafkaProducer | None = None
        
        with open("schema.avsc", "r") as schema_file:
            self.schema = avro.schema.parse(schema_file.read())

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

    def start(self):
        self.kafka_thread = threading.Thread(None, self.kafka_listen, daemon=True)
        self.retrieve_thread = threading.Thread(None, self.retrieve_skins, daemon=True)
        
        self.kafka_thread.start()
        self.retrieve_thread.start()

    @property
    def is_running(self):
        if (
            self.kafka_thread is not None
            and self.kafka_thread.is_alive()
        ):
            return True
        return False

    def kafka_listen(self):
        msg: ConsumerRecord
        consumer = self.kafka_consumer
        
        for msg in consumer:
            symbol = msg.value.decode("utf-8")

            if symbol not in self.symbols:
                print(f"Recieved new symbol: {symbol}")
                self.process_skin(symbol)

    def process_skin(self, symbol):
        if symbol is None:
            print(f"Symbol {symbol} not found")
            return
            
        self.symbols.add(symbol)

    def retrieve_skins(self):
        while True:
            if self.symbols:
                try:
                    skins = get_skins(list(self.symbols))
                    for skin in skins:
                        skin_data = to_avro_skin(skin)
                        
                        writer = avro.io.DatumWriter(self.schema)
                        bytes_writer = io.BytesIO()
                        encoder = avro.io.BinaryEncoder(bytes_writer)
                        
                        writer.write(skin_data, encoder)
                        avro_bytes = bytes_writer.getvalue()

                        self.kafka_producer.send(self.out_topic, value=avro_bytes)                     
                except Exception as e:
                    print(f"Error fecthing from OpenSkin: {e}")

            time.sleep(60) # Every minut