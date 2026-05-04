from __future__ import annotations

from dataclasses import dataclass

from .calls import compact_call_sequence, parse_call_sequence


SEATS = ("n", "e", "s", "w")
VULNERABILITY_STATES = ("none", "ns", "ew", "both")


@dataclass(frozen=True)
class Auction:
    calls: tuple[str, ...]
    dealer: str = "n"
    vulnerability: str = "none"

    @classmethod
    def parse(cls, calls: str | list[str] | tuple[str, ...], dealer: str = "n", vulnerability: str = "none") -> "Auction":
        dealer = dealer.lower()
        if dealer not in SEATS:
            raise ValueError(f"Unknown dealer: {dealer}")
        vulnerability = vulnerability.lower()
        if vulnerability not in VULNERABILITY_STATES:
            raise ValueError(f"Unknown vulnerability: {vulnerability}")
        return cls(calls=parse_call_sequence(calls), dealer=dealer, vulnerability=vulnerability)

    @property
    def actor_to_call(self) -> str:
        return self.actor_at(len(self.calls))

    def actor_at(self, index: int) -> str:
        start = SEATS.index(self.dealer)
        return SEATS[(start + index) % len(SEATS)]

    def compact_sequence(self) -> str:
        return compact_call_sequence(self.calls)

    def canonical_key(self) -> str:
        calls = self.compact_sequence()
        return f"dealer={self.dealer};vul={self.vulnerability};calls={calls}"
