from kafka import KafkaProducer


print("1. Start test - create producer")
kafkaProducer = KafkaProducer(
    bootstrap_servers="localhost:9092"
)

print("2. Connected to kafka")

kafkaProducer.send(
    "new_skin",
    value=b"AK-47 | Crane Flight (Field-Tested)"
)

print("3. Message sent")

kafkaProducer.flush()
kafkaProducer.close()
print("New skin added")