from pathlib import Path
import httpx

import avro
import avro.schema
from avro.io import DatumWriter
from avro.datafile import DataFileWriter
from datetime import datetime, timezone

class TCGDexHandler:
    def serialize(self, card) -> Path:
        # Temp test, should save to kafka topic instead of file, but for now let's just save to a file
        source_dir = Path(__file__).resolve().parent
        schema_path = source_dir / "pokemonSchema.avsc"
        output_path = source_dir / "pokemon.avro"

        schema = avro.schema.parse(schema_path.read_bytes())
        writer = DataFileWriter(
            output_path.open("wb"),
            DatumWriter(),
            schema,
        )
        try:
            writer.append(
                {
                    "id": card.id,
                    "name": card.name,
                    "serie": card.set.name,
                    "set": card.set.id,
                    "observed_at": datetime.now(timezone.utc),
                    "variants": {
                        "normal": card.variants.normal,
                        "reverse": card.variants.reverse,
                        "holo": card.variants.holo,
                        "firstEdition": card.variants.firstEdition,
                        "wPromo": card.variants.wPromo,
                    },
                    "price": self.getCardPrice(card.id),
                }
            )
        finally:
            writer.close()

        return output_path

    def getCardPrice(self, card_id: str) -> float | None:
        """Fetch the price of a card from the TCGdex API."""
        url = f"https://api.tcgdex.net/v2/en/cards/{card_id}"

        response = httpx.get(url)
        response.raise_for_status()

        data = response.json()

        pricing = data.get("pricing", {})
        return pricing.get("cardmarket", {}).get("trend", None)
