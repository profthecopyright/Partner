from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .calls import normalize_call, normalize_pattern


@dataclass(frozen=True)
class Author:
    name: str
    contact: str | None = None
    organization: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Author":
        data = data or {}
        return cls(
            name=data.get("name", "Unknown"),
            contact=data.get("contact"),
            organization=data.get("organization"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "contact": self.contact,
            "organization": self.organization,
        }


@dataclass(frozen=True)
class Gadget:
    id: str
    namespace: str
    name: str
    version: str
    author: Author
    rules: tuple["GadgetRule", ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Gadget":
        return cls.from_parts(data, data.get("rules", []))

    @classmethod
    def from_parts(cls, metadata: dict[str, Any], rule_data: list[dict[str, Any]]) -> "Gadget":
        author = Author.from_dict(metadata.get("author"))
        gadget = cls(
            id=metadata["id"],
            namespace=metadata.get("namespace", metadata["id"]),
            name=metadata["name"],
            version=metadata.get("version", "0.1.0"),
            author=author,
            rules=(),
        )
        rules = tuple(GadgetRule.from_dict(item, gadget, author) for item in rule_data)
        return cls(
            id=gadget.id,
            namespace=gadget.namespace,
            name=gadget.name,
            version=gadget.version,
            author=gadget.author,
            rules=rules,
        )

    @property
    def qualified_id(self) -> str:
        return f"{self.namespace}/{self.id}@{self.version}"


@dataclass(frozen=True)
class GadgetRule:
    id: str
    context: dict[str, Any]
    call: str
    gadget_id: str
    gadget_namespace: str
    gadget_version: str
    gadget_name: str
    author: Author
    applicability: dict[str, Any] = field(default_factory=dict)
    selection: dict[str, Any] = field(default_factory=dict)
    meaning: dict[str, Any] = field(default_factory=dict)
    semantic_effects: tuple[dict[str, Any], ...] = ()
    default_policy: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any], gadget: Gadget, inherited_author: Author) -> "GadgetRule":
        context = data.get("context", {}) or {}
        if "auction_pattern" in data and "auction_pattern" not in context:
            context = {**context, "auction_pattern": data["auction_pattern"]}
        if "auction_pattern" in context:
            context = {**context, "auction_pattern": normalize_pattern(context["auction_pattern"])}
        return cls(
            id=data["id"],
            context=context,
            call=normalize_call(data["call"]),
            gadget_id=gadget.id,
            gadget_namespace=gadget.namespace,
            gadget_version=gadget.version,
            gadget_name=gadget.name,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            applicability=data.get("applicability", {}) or {},
            selection=data.get("selection", {}) or {},
            meaning=data.get("meaning", {}) or {},
            semantic_effects=tuple(data.get("semantic_effects", []) or []),
            default_policy=bool(data.get("default_policy", False)),
        )

    @property
    def auction_pattern(self) -> str:
        return self.context.get("auction_pattern", "")

    @property
    def has_selection(self) -> bool:
        return bool(self.selection)

    @property
    def has_meaning(self) -> bool:
        return bool(self.meaning)

    @property
    def qualified_rule_id(self) -> str:
        return f"{self.gadget_namespace}/{self.gadget_id}@{self.gadget_version}:{self.id}"

    def origin_dict(self) -> dict[str, Any]:
        return {
            "namespace": self.gadget_namespace,
            "gadget_id": self.gadget_id,
            "gadget_name": self.gadget_name,
            "gadget_version": self.gadget_version,
            "rule_id": self.id,
            "qualified_rule_id": self.qualified_rule_id,
            "author": self.author.to_dict(),
        }
