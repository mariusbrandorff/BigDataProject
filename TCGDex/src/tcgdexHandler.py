import asyncio
import io
from pathlib import Path
import httpx
import threading

from dotenv import load_dotenv

import avro
import avro.schema
from datetime import datetime, timezone

#kafka imports
from kafka import KafkaConsumer, KafkaProducer
from tcgdexsdk import TCGdex

class TCGDexHandler:
    def __init__(self, in_topic: str, out_topic: str, bootstrap_servers: str):
        self.kafka_thread: threading.Thread | None = None
        self.cards: set[str] = set()

        self.in_topic = in_topic
        self.out_topic = out_topic
        self.bootstrap_servers = bootstrap_servers

        self._kafka_producer: KafkaProducer | None = None
        self._schema: avro.schema.Schema | None = None

        

        ## Kafka consumer and producer
    @property
    def kafka_consumer(self) -> KafkaConsumer:
        return KafkaConsumer(self.in_topic, bootstrap_servers=self.bootstrap_servers)
    
    

    @property
    def kafka_producer(self) -> KafkaProducer:
        if self._kafka_producer is None:
            self._kafka_producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        return self._kafka_producer

    

    @property
    def schema(self) -> avro.schema.Schema:
        """Returns the avro schema. If any changes have been made since last return, it loads the new schema."""
        if self._schema is None:
            self._schema = avro.schema.parse(open("pokemonSchema.avsc").read())
        return self._schema

    @property
    def is_running(self):
        if (
            self.kafka_thread is not None
            and self.kafka_thread.is_alive()
        ):
            return True
        return False

    # Public methods
    def start(self):
        self.kafka_thread = threading.Thread(None, self.kafka_listen, daemon=True)
        self.kafka_thread.start()

    # Serialize a card to Avro format.
    def serialize(self, card) -> bytes:
        writer = avro.io.DatumWriter(self.schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write({
                    "id": card.id,
                    "name": card.name,
                    "serie": card.set.name,
                    "set": card.set.id,
                    "observed_at": datetime.now(timezone.utc),
                    "variants": {
                        "normal": card.variants.normal,
                        "reverse": card.variants.reverse,
                        "holo": card.variants.holo,
                        "firstEdition": card.variants.firstEdition,
                        "wPromo": card.variants.wPromo,
                    },
                    "price": self.getCardPrice(card.id),
                }, encoder)
        raw_bytes = bytes_writer.getvalue()
        return bytes_writer.getvalue()

    def getCardPrice(self, card_id: str) -> float | None:
        """Fetch the price of a card from the TCGdex API."""
        url = f"https://api.tcgdex.net/v2/en/cards/{card_id}"

        response = httpx.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        pricing = data.get("pricing") or {}
        cardmarket = pricing.get("cardmarket") or {}
        return cardmarket.get("trend")

    def process_card(self, card_id: str):
        """Fetch the card data from the TCGdex API and serialize it to Avro format."""
        tcgdex = TCGdex()
        card = tcgdex.card.getSync(card_id)

        if card is None:
            print(f"Card {card_id} not found")
            return

        data = self.serialize(card)

        future = self.kafka_producer.send(self.out_topic, value = data, key = card_id.encode("utf-8"))
        future.get(timeout=10)
        self.cards.add(card_id)

    def kafka_listen(self):

        consumer = self.kafka_consumer
        for message in consumer:
            card_id = message.value.decode("utf-8")

            if card_id not in self.cards:
                print(f"Received new card ID: {card_id}")
                # Fetch the card data from the TCGdex API
                self.process_card(card_id)
