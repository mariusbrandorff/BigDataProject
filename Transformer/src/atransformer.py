from abc import abstractmethod
from threading import Thread
from typing import ByteString
from kafka import KafkaConsumer, KafkaProducer
from kafka.consumer.fetcher import ConsumerRecord
from hdfs import InsecureClient
import hashlib

import pandas as pd

class ATransformer:
    """docstring for ATransformer."""


    in_topic: str
    bootstrap_servers: str
    hdfs_host: str


    def __init__(self, in_topic: str, bootstrap_servers: str, hdfs_host: str):
        self.in_topic = in_topic
        self.bootstrap_servers = bootstrap_servers
        self.hdfs_host = hdfs_host


    _kafka_consumer: KafkaConsumer | None = None
    
    @property
    def kafka_consumer(self) -> KafkaConsumer:
        if self._kafka_consumer == None:
            self._kafka_consumer = KafkaConsumer(
                self.in_topic, bootstrap_servers=self.bootstrap_servers
            )
        return self._kafka_consumer
    
    
    _hdfs: InsecureClient | None = None

    @property
    def hdfs(self) -> InsecureClient:
        if self._hdfs == None:
            self._hdfs = InsecureClient(self.hdfs_host, "root")
        return self._hdfs


    _topic_name: str | None = None

    @property
    def topic_name(self) -> str:
        if self._topic_name == None:
            self._topic_name = self.in_topic[:-4] # Remove _out
        return self._topic_name


    def run(self):
        msg: ConsumerRecord

        for msg in self.kafka_consumer:
            if not isinstance(msg, ConsumerRecord):
                print("Something wrong!?")
                raise Exception(
                    "Message from kafka wasn't the expected type: ConsumerRecord"
                )

            Thread(self.handle_message(msg), daemon=True).start()


    def handle_message(self, msg: ConsumerRecord):
        """Handles types and conversions, saves avro and transforms avro to parquet"""
        
        avro_thread = Thread(None, self.save_avro(msg.value))
        parquet_thread = Thread(None, self.save_parquet())

        avro_thread.start()
        parquet_thread.start()

        avro_thread.join()
        parquet_thread.join()


    def avro_name(self, value: ByteString) -> str:
        print(value)
        file_hash = hashlib.sha256(value).hexdigest()
        return f"{file_hash}.avro"
    
    def save_avro(self, value: ByteString):
        name = self.avro_name(value)
        self.hdfs.write(f"/ingestion/avro/{self.topic_name}/{name}", data=value)


    def prune_parquet(self, parquet):
        return parquet


    def save_parquet(self):
        formatted = self.prune_parquet("")
        pass