from argparse import ArgumentParser
import asyncio
from kafka_watch import main as kafkamain, parse as kafkaparse
from regular import main as cronmain

# Don't touch, I will do this :)

async def main():
    parser = ArgumentParser()
    parser.add_argument("-b", "--bootstrap-server", type=str, default="localhost:9092")

    kafkaparse(parser)


    args = parser.parse_args()
    # Run a listener for kafka
    await kafkamain(args.in_topic, args.out_topic, args.bootstrap_server)
    # Run a cron job worker
    await cronmain()

if __name__ == "__main__":
    asyncio.run(main())
