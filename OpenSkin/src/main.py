import time

from openskinhandler import OpenSkinHandler

kafkaHandler = OpenSkinHandler(
        in_topic="new_skin",
        out_topic="track_skin",
        bootstrap_servers="localhost:9092"
    )

kafkaHandler.start()

try:
    while True:
        print("hallo hallo er der signal i røret:", kafkaHandler.is_running)
        time.sleep(5)
    
except Exception as e:
    print(f"Åh nej, de lagde på: {e}")