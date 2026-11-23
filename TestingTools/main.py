from argparse import ArgumentParser
from pathlib import PurePath
from typing import Any, List, Type

from kafka import KafkaConsumer, KafkaProducer
from kafka.consumer.fetcher import ConsumerRecord
from textual import on
from textual.app import App, ComposeResult
from textual.containers import VerticalGroup
from textual.driver import Driver
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, Input, Log

from threading import Event

class Logs(Log):
    def __init__(self, topic: str, bootstrap_server: str) -> None:
        super().__init__()
        self.topic = topic
        self.bootstrap_server = bootstrap_server
        self._stop = Event()

    def on_mount(self) -> None:
        self.run_worker(self.kafka_listen, exclusive=True, thread=True)

    def on_unmount(self) -> None:
        self._stop.set()

    def kafka_listen(self) -> None:
        consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_server,
            auto_offset_reset="earliest",
            consumer_timeout_ms=500,
        )

        try:
            while not self._stop.is_set():
                for msg in consumer:
                    if self._stop.is_set():
                        break
                    if isinstance(msg.value, bytes):
                        text: str
                        try:
                            text = msg.value.decode("utf-8")
                        except:
                            text = str(msg.value)
                        self.app.call_from_thread(self.write_line, text)
        finally:
            consumer.close()

        

class TestingApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    KAFKAPRODUCER: KafkaProducer

    in_topic: str
    out_topic: str
    bootstrap_server: str

    def __init__(self, in_topic: str, out_topic: str, bootstrap_server: str, driver_class: type[Driver] | None = None, css_path: str | PurePath | List[str | PurePath] | None = None, watch_css: bool = False, ansi_color: bool | None = None):
        super().__init__(driver_class, css_path, watch_css, ansi_color)

        self.in_topic = in_topic
        self.out_topic = out_topic
        self.bootstrap_server = bootstrap_server

        self.KAFKAPRODUCER = KafkaProducer(bootstrap_servers=self.bootstrap_server)
        

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Logs(self.in_topic, self.bootstrap_server)
        yield Input(placeholder="Type anything to send to out_topic here...")
        yield Footer()

    @on(Input.Submitted)
    def send_message(self, event: Input.Submitted) -> None:
        self.log(event.value)
        self.KAFKAPRODUCER.send(self.out_topic, event.value.encode("utf-8"))
        self.query_exactly_one(Input).value = ""
        
    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-i", "--in_topic", dest="in_topic")
    parser.add_argument("-o", "--out_topic", dest="out_topic")
    parser.add_argument("-b", "--bootstrap_server", dest="bootstrap_server", default="localhost:9092")

    args = parser.parse_args()

    app = TestingApp(args.in_topic, args.out_topic, args.bootstrap_server)
    app.run()