from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .auction import Auction
from .cards import Hand
from .evaluator import evaluate, evaluate_selection
from .gadget import GadgetRule
from .matcher import historical_pattern_for, matches_context, matches_pattern
from .trace import SemanticFact, SemanticTrace


@dataclass(frozen=True)
class Candidate:
    call: str
    origin: dict[str, Any]
    public_meaning: dict[str, Any]
    algorithm: str
    rule_id: str
    score: int
    criteria_results: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class Selection:
    call: str | None
    selected: Candidate | None
    candidates: tuple[Candidate, ...]
    trace: SemanticTrace


def choose_bid(rules: list[GadgetRule], auction: Auction, hand: Hand, environment: dict | None = None) -> Selection:
    trace = replay_auction(rules, auction, hand, environment)
    candidates = []
    active_environment = environment or {}
    for rule in rules:
        if rule.default_policy or not rule.has_selection or not matches_context(rule.context, auction):
            continue
        if not evaluate(rule.applicability, hand, trace, active_environment):
            continue
        if not evaluate(rule.selection.get("applicability", {}), hand, trace, active_environment):
            continue
        candidate = _candidate(rule, hand, trace, active_environment)
        if candidate is not None:
            candidates.append(candidate)
    candidates = tuple(candidates)

    if not candidates:
        fallback = _default_candidate(rules, auction, hand, trace, environment)
        trace.warn(f"No matching selection rule for auction: {auction.compact_sequence()}; defaulting to {fallback.call}")
        return Selection(call=fallback.call, selected=fallback, candidates=(fallback,), trace=trace)

    ordered = sorted(candidates, key=lambda candidate: candidate.score, reverse=True)
    if len(ordered) > 1 and ordered[0].score == ordered[1].score:
        trace.warn(f"Ambiguous top score for {ordered[0].call} and {ordered[1].call}")

    best = ordered[0]
    return Selection(call=best.call, selected=best, candidates=tuple(ordered), trace=trace)


def replay_auction(rules: list[GadgetRule], auction: Auction, hand: Hand | None = None, environment: dict | None = None) -> SemanticTrace:
    trace = SemanticTrace()
    for index, call in enumerate(auction.calls):
        if call == "P":
            continue
        pattern = historical_pattern_for(auction.calls, index)
        prior_auction = Auction(calls=auction.calls[:index], dealer=auction.dealer, vulnerability=auction.vulnerability)
        active_environment = environment or {}
        matches = [rule for rule in rules if rule.has_meaning and matches_context(rule.context, prior_auction) and rule.call == call]
        if hand is not None:
            matches = [rule for rule in matches if evaluate(rule.applicability, hand, trace, active_environment)]
        if not matches:
            trace.warn(f"Undefined historical call {call} at auction position {index + 1}")
            continue
        if len(matches) > 1:
            trace.warn(f"Ambiguous historical call {call} at auction position {index + 1}")
        rule = matches[0]
        origin = rule.origin_dict()
        for effect in rule.semantic_effects:
            trace.add_fact(SemanticFact.from_dict(effect, origin))
        trace.add_applied_meaning_rule(
            {
                "call": call,
                "auction_pattern": pattern,
                "origin": origin,
                "public_meaning": rule.meaning,
            }
        )
    return trace


def _candidate(rule: GadgetRule, hand: Hand, trace: SemanticTrace, environment: dict | None) -> Candidate | None:
    evaluation = evaluate_selection(rule.selection, hand, trace, environment)
    if not evaluation["eligible"]:
        return None
    return Candidate(
        call=rule.call,
        origin=rule.origin_dict(),
        public_meaning=rule.meaning,
        algorithm=evaluation["algorithm"],
        rule_id=rule.id,
        score=evaluation["score"],
        criteria_results=tuple(evaluation["criteria_results"]),
    )


def _default_candidate(rules: list[GadgetRule], auction: Auction, hand: Hand, trace: SemanticTrace, environment: dict | None) -> Candidate:
    for rule in rules:
        if not rule.default_policy:
            continue
        if rule.auction_pattern != "*" and not matches_pattern(rule.auction_pattern, auction):
            continue
        candidate = _candidate_from_default_rule(rule)
        if candidate is not None:
            return candidate
    return _default_pass_candidate()


def _candidate_from_default_rule(rule: GadgetRule) -> Candidate | None:
    return Candidate(
        call=rule.call,
        origin=rule.origin_dict(),
        public_meaning=rule.meaning,
        algorithm="default_policy",
        rule_id=rule.id,
        score=0,
        criteria_results=(),
    )


def _default_pass_candidate() -> Candidate:
    return Candidate(
        call="P",
        origin={
            "namespace": "default",
            "gadget_id": "default_policy",
            "gadget_name": "Default Policy",
            "gadget_version": "0.0.1",
            "rule_id": "default_pass",
            "qualified_rule_id": "default/default_policy@0.0.1:default_pass",
            "author": {
                "name": "Meow Li",
                "contact": None,
                "organization": None,
            },
        },
        public_meaning={
            "call_nature": "default",
            "action_type": "fallback_pass",
            "alertable": False,
        },
        algorithm="default_policy",
        rule_id="default_pass",
        score=0,
        criteria_results=(),
    )
