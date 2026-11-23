import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass
class Skin:
    item: str
    icon_url: str
    prices: dict[str, Any]
    links: dict[str, str]
    lowest_ask: dict[str, Any]
    updated_at: datetime

def parse_datetime(value: str) -> datetime:
    if "T" in value:  # e.g. 2026-11-17T19:15:19Z
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return datetime.strptime(value, "%Y.%m.%d %H:%M:%S")


def json_to_skin(js: dict[str, Any]) -> Skin:
    return Skin(
        item=js["item"],
        icon_url=js["icon_url"],
        prices=js["prices"],
        links=js["links"],
        lowest_ask=js["lowest_ask"],
        updated_at=parse_datetime(js["updated_at"]),
    )
    
def to_avro_skin(skin: Skin):
    data = asdict(skin)

    data["prices"] = json.dumps(data["prices"])

    for field in ("updated_at",):
        value = data[field]
        
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        
        data[field] = value

    return data