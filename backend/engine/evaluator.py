from __future__ import annotations

from typing import Any

from .cards import Hand
from .trace import SemanticTrace


def evaluate(condition: dict[str, Any], hand: Hand, trace: SemanticTrace, environment: dict[str, Any] | None = None) -> bool:
    if not condition:
        return True

    environment = environment or {}

    if "all" in condition:
        return all(evaluate(item, hand, trace, environment) for item in condition["all"])

    if "any" in condition:
        return any(evaluate(item, hand, trace, environment) for item in condition["any"])

    if "not" in condition:
        return not evaluate(condition["not"], hand, trace, environment)

    if "fact_exists" in condition:
        return trace.fact_exists(condition["fact_exists"])

    for key, expected in condition.items():
        actual = _resolve_value(key, hand, trace, environment)
        if not _compare(actual, expected):
            return False
    return True


def _resolve_value(key: str, hand: Hand, trace: SemanticTrace, environment: dict[str, Any]) -> Any:
    if key == "self.hcp":
        return hand.hcp
    if key == "self.balanced":
        return hand.balanced
    if key.startswith("self."):
        suit = key.removeprefix("self.")
        return hand.length(suit)
    if key.startswith("env."):
        return environment.get(key.removeprefix("env."))
    raise ValueError(f"Unsupported condition key: {key}")


def _compare(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        if "min" in expected and actual < expected["min"]:
            return False
        if "max" in expected and actual > expected["max"]:
            return False
        if "eq" in expected and actual != expected["eq"]:
            return False
        if "in" in expected and actual not in expected["in"]:
            return False
        return True
    return actual == expected


def evaluate_selection(selection: dict[str, Any], hand: Hand, trace: SemanticTrace, environment: dict[str, Any] | None = None) -> dict[str, Any]:
    environment = environment or {}
    algorithm = selection.get("algorithm", "weighted_score")
    if algorithm != "weighted_score":
        raise ValueError(f"Unsupported selection algorithm: {algorithm}")

    score = 0
    eligible = True
    criteria_results = []
    for criterion in selection.get("criteria", []):
        result = evaluate_criterion(criterion, hand, trace, environment)
        if criterion.get("required", True) and not result["passed"]:
            eligible = False
        if result["passed"]:
            score += result["contribution"]
        criteria_results.append(result)

    return {
        "algorithm": algorithm,
        "eligible": eligible,
        "score": score,
        "criteria_results": criteria_results,
    }


def evaluate_criterion(criterion: dict[str, Any], hand: Hand, trace: SemanticTrace, environment: dict[str, Any]) -> dict[str, Any]:
    evaluator = criterion["evaluator"]
    value = None
    passed = False

    if evaluator == "range_contains":
        value = _resolve_value(criterion["input"], hand, trace, environment)
        passed = _compare(value, {"min": criterion.get("min"), "max": criterion.get("max")})
    elif evaluator == "min_value":
        value = _resolve_value(criterion["input"], hand, trace, environment)
        passed = value >= criterion["min"]
    elif evaluator == "equals":
        value = _resolve_value(criterion["input"], hand, trace, environment)
        passed = value == criterion["value"]
    elif evaluator == "fact_exists":
        value = criterion["query"]
        passed = trace.fact_exists(criterion["query"])
    else:
        raise ValueError(f"Unsupported criterion evaluator: {evaluator}")

    return {
        "criterion_id": criterion["criterion_id"],
        "evaluator": evaluator,
        "passed": passed,
        "required": criterion.get("required", True),
        "value": value,
        "contribution": int(criterion.get("weight", 0)) if passed else 0,
    }
