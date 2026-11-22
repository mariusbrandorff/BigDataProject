import json
from kafka import KafkaProducer

class KafkaProducer:

    bootstrap_servers: str
    producer: KafkaProducer

    def __init__(bootstrap_servers: str):
        bootstrap_servers = bootstrap_servers
        producer = KafkaProducer(bootstrap_servers = bootstrap_servers)

    @property
    def kafka_producer(self) -> KafkaProducer:
        if self.producer is None:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers
            )
        return self.producer