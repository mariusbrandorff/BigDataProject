import enum
from datetime import datetime
from typing import Any, Optional, TypedDict

from sqlalchemy import JSON, Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

base = declarative_base()


# ---------------------------------------------------------------- enums
class CardCategory(str, enum.Enum):
    POKEMON = "Pokemon"
    TRAINER = "Trainer"
    ENERGY = "Energy"


class CardStage(str, enum.Enum):
    BASIC = "Basic"
    STAGE1 = "Stage1"
    STAGE2 = "Stage2"
    VMAX = "VMAX"
    VSTAR = "VSTAR"
    MEGA = "MEGA"
    BREAK = "BREAK"
    LEVEL_UP = "Level-Up"
    RESTORED = "Restored"


# ------------------------------------------- shapes of the JSON columns
class Attack(TypedDict, total=False):
    cost: list[str]
    name: str
    effect: str
    damage: int | str  # API gives ints (90) but also "30+", "x20", ...


class TypeModifier(TypedDict):
    type: str
    value: str  # e.g. "×2", "-30"


class VariantDetail(TypedDict, total=False):
    type: str  # normal | reverse | holo | firstEdition | wPromo
    size: str
    thirdParty: dict[str, int]
    variantId: str
    pricing: dict[str, Any]


# ---------------------------------------------------------------- model
class PokemonCardInfo(base):
    __tablename__ = "PokemonCardInfos"

    # Identity
    id: Mapped[str] = mapped_column(String(32), primary_key=True)  # "swsh3-136"
    local_id: Mapped[str] = mapped_column(String(16), index=True)  # kept as str: "TG01", "SWSH001"
    name: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[CardCategory] = mapped_column(Enum(CardCategory), index=True)
    rarity: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    illustrator: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Set (flattened from the nested "set" object)
    set_id: Mapped[str] = mapped_column(String(32), index=True)
    set_name: Mapped[str] = mapped_column(String(128))
    set_logo: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    set_symbol: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    set_card_count_official: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    set_card_count_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Variants (flags + detailed list incl. per-variant pricing)
    has_normal: Mapped[bool] = mapped_column(Boolean, default=False)
    has_reverse: Mapped[bool] = mapped_column(Boolean, default=False)
    has_holo: Mapped[bool] = mapped_column(Boolean, default=False)
    has_first_edition: Mapped[bool] = mapped_column(Boolean, default=False)
    has_w_promo: Mapped[bool] = mapped_column(Boolean, default=False)
    variants_detailed: Mapped[list[VariantDetail]] = mapped_column(JSON, default=list)

    # Gameplay (nullable: Trainer/Energy cards don't have most of these)
    dex_ids: Mapped[Optional[list[int]]] = mapped_column(JSON, nullable=True)
    hp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    types: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    stage: Mapped[Optional[CardStage]] = mapped_column(Enum(CardStage), nullable=True)
    evolve_from: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    attacks: Mapped[Optional[list[Attack]]] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[Optional[list[TypeModifier]]] = mapped_column(JSON, nullable=True)
    resistances: Mapped[Optional[list[TypeModifier]]] = mapped_column(JSON, nullable=True)
    retreat: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Legality
    regulation_mark: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    legal_standard: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    legal_expanded: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Pricing (cardmarket = EUR, tcgplayer = USD; stored as returned by the API)
    pricing: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Source timestamp
    updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "PokemonCardInfo":
        """Build an instance from a TCGdex card payload."""
        card_set = data.get("set", {})
        counts = card_set.get("cardCount", {})
        variants = data.get("variants", {})
        legal = data.get("legal", {})
        updated = data.get("updated")
        stage = data.get("stage")

        return cls(
            id=data["id"],
            local_id=str(data["localId"]),
            name=data["name"],
            category=CardCategory(data["category"]),
            rarity=data.get("rarity"),
            illustrator=data.get("illustrator"),
            image=data.get("image"),
            description=data.get("description"),
            set_id=card_set["id"],
            set_name=card_set["name"],
            set_logo=card_set.get("logo"),
            set_symbol=card_set.get("symbol"),
            set_card_count_official=counts.get("official"),
            set_card_count_total=counts.get("total"),
            has_normal=variants.get("normal", False),
            has_reverse=variants.get("reverse", False),
            has_holo=variants.get("holo", False),
            has_first_edition=variants.get("firstEdition", False),
            has_w_promo=variants.get("wPromo", False),
            variants_detailed=data.get("variants_detailed", []),
            dex_ids=data.get("dexId"),
            hp=data.get("hp"),
            types=data.get("types"),
            stage=CardStage(stage) if stage else None,
            evolve_from=data.get("evolveFrom"),
            attacks=data.get("attacks"),
            weaknesses=data.get("weaknesses"),
            resistances=data.get("resistances"),
            retreat=data.get("retreat"),
            regulation_mark=data.get("regulationMark"),
            legal_standard=legal.get("standard", False),
            legal_expanded=legal.get("expanded", False),
            pricing=data.get("pricing"),
            updated=datetime.fromisoformat(updated) if updated else None,
        )