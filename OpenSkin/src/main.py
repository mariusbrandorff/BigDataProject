from argparse import ArgumentParser
import time

from openskinhandler import OpenSkinHandler
from envdefault import EnvDefault

def main():
    parser = ArgumentParser()

    parser.add_argument(
        "-b",
        "--bootstrap-server",
        dest="bootstrap_server",
        action=EnvDefault,
        envvar="BOOTSTRAP_SERVER",
        help="Kafka bootstrap server"
    )

    parser.add_argument(
        "-i",
        "--in",
        dest="in_topic",
        action=EnvDefault,
        envvar="IN_TOPIC",
        help="Input topic for Openskin"
    )  

    parser.add_argument(
        "-o",
        "--out",
        dest="out_topic",
        action=EnvDefault,
        envvar="OUT_TOPIC",
        help="Output topic for Openskin"
    )   

    args = parser.parse_args()

    kafkaHandler = OpenSkinHandler(
        in_topic=args.in_topic,
        out_topic=args.out_topic,
        bootstrap_servers=args.bootstrap_server
    )

    kafkaHandler.start()

    try:
        while True:
            print("hallo hallo er der signal i røret:", kafkaHandler.is_running)
            time.sleep(5)
        
    except Exception as e:
        print(f"Åh nej, de lagde på: {e}")

if __name__ == "__main__":
    main()