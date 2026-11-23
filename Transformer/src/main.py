
from argparse import ArgumentParser
from threading import Thread

from envdefault import EnvDefault
from biquote import BiquoteTransformer
from openskin import OpenSkinTransformer
from tcgdex import TCGDexTransformer

topic_format = "{TOPIC}_out"

def main():
    parser = ArgumentParser()

    topics = [
        "biquote",
        "openskin",
        "tcgdex"
    ]

    for topic in topics:
        parser.add_argument(
            f"-{topic[0]}",
            f"--{topic}-topic",
            dest=f"{topic}_topic",
            action=EnvDefault,
            envvar=f"{topic.upper()}_TOPIC",
            help=f"Specify the topic for {topic} (can also be specified using {topic.upper()}_TOPIC environment variable)",
            default=topic_format.replace("{TOPIC}", topic)
        )

    parser.add_argument(
        "--bootstrap-servers",
        dest="bootstrap_servers",
        action=EnvDefault,
        envvar="BOOTSTRAP_SERVERS",
        help="Specify the hostname for kafkas bootstrap servers (can also be specified using BOOTSTRAP_SERVERS environment variable)"
    )

    parser.add_argument(
        "--hdfs-host",
        dest="hdfs_host",
        action=EnvDefault,
        envvar="HDFS_HOST",
        help="Specify the hostname for hdfs (can also be specified using HDFS_HOST environment variable)"
    )
    
    args = parser.parse_args()

    biquote = BiquoteTransformer(args.biquote_topic, args.bootstrap_servers, args.hdfs_host)
    open_skin = OpenSkinTransformer(args.openskin_topic, args.bootstrap_servers, args.hdfs_host)
    tcg_dex = TCGDexTransformer(args.tcgdex_topic, args.bootstrap_servers, args.hdfs_host)

    threads = [
        Thread(None, biquote.run()),
        Thread(None, open_skin.run()),
        Thread(None, tcg_dex.run())
    ]

    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()