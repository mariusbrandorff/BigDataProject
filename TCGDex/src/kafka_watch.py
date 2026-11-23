from argparse import ArgumentParser
import asyncio

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord

from envdefault import EnvDefault
from tcgdexHandler import TCGDexHandler

# Default needs

def parse(parser: ArgumentParser):
    parser.add_argument(
        "-i", "--in", dest="in_topic",
        action=EnvDefault, envvar='IN_TOPIC',
        help="Specify the in topic to process (can also be specified using IN_TOPIC environment variable)"
    )
    parser.add_argument(
        "-o", "--out", dest="out_topic",
        action=EnvDefault, envvar='OUT_TOPIC',
        help="Specify the out topic to process (can also be specified using OUT_TOPIC environment variable)"
    )

async def main(in_topic: str, out_topic: str, bootstrap_servers: str):
    handler = TCGDexHandler(in_topic, out_topic, bootstrap_servers)
    handler.start()

    while handler.is_running:
        await asyncio.sleep(10) # 10s

# ?



if __name__ == "__main__":
    parser = ArgumentParser()
    parse(parser)

    args = parser.parse_args()

    asyncio.run(main(args.in_topic, args.out_topic, "localhost:9092"))