from __future__ import annotations

from dataclasses import dataclass


RANK_POINTS = {
    "A": 4,
    "K": 3,
    "Q": 2,
    "J": 1,
}

SUITS = ("spades", "hearts", "diamonds", "clubs")
SUIT_MARKERS = {
    "S": "spades",
    "H": "hearts",
    "D": "diamonds",
    "C": "clubs",
}
VALID_RANKS = set("AKQJT98765432X")


@dataclass(frozen=True)
class Hand:
    spades: str
    hearts: str
    diamonds: str
    clubs: str

    @classmethod
    def parse(cls, data: str, validate_count: bool = True) -> "Hand":
        if isinstance(data, str):
            return cls.from_compact(data, validate_count=validate_count)
        raise TypeError("Hand input must be a compact string")

    @classmethod
    def from_dict(cls, data: dict[str, str], validate_count: bool = False) -> "Hand":
        hand = cls(
            spades=_normalize_suit(data.get("spades", "")),
            hearts=_normalize_suit(data.get("hearts", "")),
            diamonds=_normalize_suit(data.get("diamonds", "")),
            clubs=_normalize_suit(data.get("clubs", "")),
        )
        hand.validate(validate_count=validate_count)
        return hand

    @classmethod
    def from_compact(cls, text: str, validate_count: bool = True) -> "Hand":
        sections = _parse_compact_sections(text)
        hand = cls.from_dict(sections, validate_count=False)
        hand.validate(validate_count=validate_count)
        return hand

    @property
    def hcp(self) -> int:
        return sum(RANK_POINTS.get(rank, 0) for suit in self.suits.values() for rank in suit)

    @property
    def suits(self) -> dict[str, str]:
        return {
            "spades": self.spades,
            "hearts": self.hearts,
            "diamonds": self.diamonds,
            "clubs": self.clubs,
        }

    def length(self, suit: str) -> int:
        if suit not in SUITS:
            raise ValueError(f"Unknown suit: {suit}")
        return len(getattr(self, suit))

    @property
    def balanced(self) -> bool:
        lengths = sorted((self.length(suit) for suit in SUITS), reverse=True)
        return lengths in ([5, 3, 3, 2], [4, 4, 3, 2], [4, 3, 3, 3])

    def validate(self, validate_count: bool = True) -> None:
        total = 0
        seen_cards = set()
        for suit_name, cards in self.suits.items():
            total += len(cards)
            for rank in cards:
                if rank == "X":
                    continue
                card = (suit_name, rank)
                if card in seen_cards:
                    raise ValueError(f"Repeated card: {rank} of {suit_name}")
                seen_cards.add(card)
        if validate_count and total != 13:
            raise ValueError(f"Wrong number of cards: expected 13, got {total}")


def _normalize_suit(cards: str) -> str:
    normalized = cards.strip().upper().replace("10", "T")
    if normalized == "-":
        return ""
    if "-" in normalized:
        raise ValueError("Void marker '-' cannot be combined with cards")
    invalid = [rank for rank in normalized if rank not in VALID_RANKS]
    if invalid:
        raise ValueError(f"Invalid card rank(s): {''.join(invalid)}")
    return normalized


def _parse_compact_sections(text: str) -> dict[str, str]:
    value = text.strip().upper()
    if not value:
        raise ValueError("Hand string is empty")

    sections = {suit: "" for suit in SUITS}
    current_suit = None
    index = 0
    while index < len(value):
        char = value[index]
        if char.isspace():
            index += 1
            continue
        if char in SUIT_MARKERS:
            current_suit = SUIT_MARKERS[char]
            index += 1
            continue
        if current_suit is None:
            raise ValueError(f"Rank appears before suit marker at position {index + 1}")
        if char == "1":
            if index + 1 < len(value) and value[index + 1] == "0":
                sections[current_suit] += "T"
                index += 2
                continue
            raise ValueError(f"Unknown symbol '1' at position {index + 1}; use 10 or T")
        if char == "-":
            next_index = index + 1
            while next_index < len(value) and value[next_index].isspace():
                next_index += 1
            if sections[current_suit] or (next_index < len(value) and value[next_index] not in SUIT_MARKERS):
                raise ValueError("Void marker '-' cannot be combined with cards")
            index += 1
            continue
        if char not in VALID_RANKS:
            raise ValueError(f"Unknown symbol '{char}' at position {index + 1}")
        sections[current_suit] += char
        index += 1

    return sections
