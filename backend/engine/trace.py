from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SemanticFact:
    fact_type: str
    attributes: dict[str, Any]
    origin: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any], origin: dict[str, Any]) -> "SemanticFact":
        attributes = dict(data)
        fact_type = str(attributes.pop("fact_type"))
        return cls(fact_type=fact_type, attributes=attributes, origin=origin)

    def matches(self, query: dict[str, Any]) -> bool:
        for key, expected in query.items():
            if key == "fact_type":
                actual = self.fact_type
            else:
                actual = self.attributes.get(key)
            if actual != expected:
                return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "fact_type": self.fact_type,
            **self.attributes,
            "origin": self.origin,
        }


@dataclass
class SemanticTrace:
    facts: list[SemanticFact] = field(default_factory=list)
    applied_meaning_rules: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)

    def add_fact(self, fact: SemanticFact) -> None:
        self.facts.append(fact)

    def fact_exists(self, query: dict[str, Any]) -> bool:
        return any(fact.matches(query) for fact in self.facts)

    def matching_facts(self, query: dict[str, Any]) -> list[SemanticFact]:
        return [fact for fact in self.facts if fact.matches(query)]

    def add_applied_meaning_rule(self, entry: dict[str, Any]) -> None:
        self.applied_meaning_rules.append(entry)

    def warn(self, text: str) -> None:
        self.diagnostics.append(text)
