from argparse import ArgumentParser
import asyncio

from biquotehandler import BiquoteHandler
from envdefault import EnvDefault

# Don't touch, I will do this :)


async def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-b", "--bootstrap-server", dest="bootstrap", type=str, default="localhost:9092"
    )

    parser.add_argument(
        "-i",
        "--in",
        dest="in_topic",
        action=EnvDefault,
        envvar="IN_TOPIC",
        help="Specify the in topic to process (can also be specified using IN_TOPIC environment variable)",
    )
    parser.add_argument(
        "-o",
        "--out",
        dest="out_topic",
        action=EnvDefault,
        envvar="OUT_TOPIC",
        help="Specify the out topic to process (can also be specified using OUT_TOPIC environment variable)",
    )

    args = parser.parse_args()

    handler = BiquoteHandler(args.in_topic, args.out_topic, args.bootstrap)

    await handler.start()
    while handler.is_running:
        await asyncio.sleep(10)  # Timeout argument?


if __name__ == "__main__":
    asyncio.run(main())
