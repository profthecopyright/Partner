from __future__ import annotations

from dataclasses import dataclass


SUITS = ("C", "D", "H", "S", "N")
SPECIAL_CALLS = ("P", "X", "R")
SUIT_RANK = {suit: index for index, suit in enumerate(SUITS)}


@dataclass(frozen=True)
class ContractBid:
    level: int
    suit: str

    @classmethod
    def parse(cls, call: str) -> "ContractBid":
        canonical = normalize_call(call)
        if not is_contract_bid(canonical):
            raise ValueError(f"Not a contract bid: {call}")
        return cls(level=int(canonical[0]), suit=canonical[1])

    @property
    def rank(self) -> int:
        return (self.level - 1) * len(SUITS) + SUIT_RANK[self.suit]

    def __str__(self) -> str:
        return f"{self.level}{self.suit}"


def normalize_call(call: str) -> str:
    value = str(call).strip().upper()
    if value == "PASS":
        return "P"
    if value == "DBL":
        return "X"
    if value == "XX":
        return "R"
    if len(value) == 3 and value.endswith("NT") and value[0] in "1234567":
        return f"{value[0]}N"
    if value in SPECIAL_CALLS:
        return value
    if is_contract_bid(value):
        return value
    raise ValueError(f"Invalid call expression: {call}")


def parse_call_sequence(sequence: str | list[str] | tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(sequence, (list, tuple)):
        return tuple(normalize_call(call) for call in sequence)

    value = str(sequence).upper()
    calls = []
    index = 0
    while index < len(value):
        char = value[index]
        if char.isspace():
            index += 1
            continue
        if value.startswith("PASS", index):
            calls.append("P")
            index += 4
            continue
        if value.startswith("DBL", index):
            calls.append("X")
            index += 3
            continue
        if value.startswith("XX", index):
            calls.append("R")
            index += 2
            continue
        if char in SPECIAL_CALLS:
            calls.append(char)
            index += 1
            continue
        if char in "1234567":
            if index + 1 >= len(value):
                raise ValueError(f"Incomplete contract call at position {index + 1}")
            suit = value[index + 1]
            if suit == "N" and index + 2 < len(value) and value[index + 2] == "T":
                calls.append(f"{char}N")
                index += 3
                continue
            if suit in SUITS:
                calls.append(f"{char}{suit}")
                index += 2
                continue
            raise ValueError(f"Invalid contract suit '{suit}' at position {index + 2}")
        raise ValueError(f"Invalid call-sequence symbol '{char}' at position {index + 1}")
    return tuple(calls)


def normalize_pattern(pattern: str) -> str:
    if pattern.strip() == "*":
        return "*"
    return compact_call_sequence(parse_call_sequence(pattern))


def compact_call_sequence(calls: tuple[str, ...]) -> str:
    return "".join(calls)


def is_contract_bid(call: str) -> bool:
    return len(call) == 2 and call[0] in "1234567" and call[1] in SUITS


def compare_contract_bids(left: str, right: str) -> int:
    left_bid = ContractBid.parse(left)
    right_bid = ContractBid.parse(right)
    return left_bid.rank - right_bid.rank
