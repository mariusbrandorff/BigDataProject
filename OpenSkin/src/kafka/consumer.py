import json
from kafka import KafkaConsumer

class KafkaConsumer:
   
    in_topic: str
    bootstrap_servers: str
    consumer: KafkaConsumer

    def __init__(self, in_topic: str, bootstrap_servers: str):
        self.in_topic = in_topic
        self.bootstrap_servers = bootstrap_servers
        self.consumer = kafka_consumer(self)

    @property
        def kafka_consumer(self) -> KafkaConsumer:
            return KafkaConsumer(self.in_topic, bootstrap_servers=self.bootstrap_servers)
