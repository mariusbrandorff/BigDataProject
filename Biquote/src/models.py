from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class Tick:
    symbol: str
    bid: float
    ask: float
    last: float
    volume: int
    timestamp: datetime
    source: str
    high: float
    low: float
    direction: str
    dayDiffPercent: float
    description: str
    time: datetime
    exchange: str
    spread: float
    mid: float


def parse_datetime(value: str) -> datetime:
    if "T" in value:  # e.g. 2026-11-17T19:15:19Z
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return datetime.strptime(value, "%Y.%m.%d %H:%M:%S")


def json_to_tick(js: dict[str, Any]) -> Tick:
    return Tick(
        **{
            **js,
            "timestamp": parse_datetime(js["timestamp"]),
            "time": parse_datetime(js["time"]),
        }
    )

def to_avro_tick(tick):
    data = asdict(tick)

    for field in ("timestamp", "time"):
        value = data[field]

        # This assumes it represents UTC
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        data[field] = value

    return data