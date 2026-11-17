from argparse import ArgumentParser
import asyncio
from contextlib import closing
import logging

from signalrcore.aio.aio_hub_connection_builder import AIOHubConnectionBuilder
from signalrcore.transport.base_transport import TransportState


# Don't touch, I will do this :)

async def main():
    parser = ArgumentParser()
    parser.add_argument("-b", "--bootstrap-server", type=str, default="localhost:9092")

    conn = AIOHubConnectionBuilder()\
        .with_url("https://biquote.io/hubs/tick")\
        .configure_logging(logging.DEBUG)\
        .build()
    
    conn.on_open(lambda: print("connection opened and handshake received ready to send messages"))
    conn.on_close(lambda: print("connection closed"))
    conn.on_error(lambda e: print(e))
    conn.on("ReceiveTick", print)
    
    await conn.start()

    await conn.wait_until_state(TransportState.connected, timeout=10)

    symbols = ['EURUSD']
    await conn.send("Subscribe", [symbols])


    await asyncio.sleep(30)
    await conn.stop()



if __name__ == "__main__":
    asyncio.run(main())
