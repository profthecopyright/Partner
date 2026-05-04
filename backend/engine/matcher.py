from __future__ import annotations

from .auction import Auction
from .calls import compact_call_sequence, normalize_pattern, parse_call_sequence


SEAT_POSITION_PASSES = {
    1: (),
    2: ("P",),
    3: ("P", "P"),
    4: ("P", "P", "P"),
}


def matches_context(context: dict, auction: Auction) -> bool:
    return matches_pattern(context.get("auction_pattern", ""), auction, context.get("seat_positions"))


def matches_pattern(pattern: str, auction: Auction, seat_positions: list[int] | tuple[int, ...] | None = None) -> bool:
    normalized_pattern = normalize_pattern(pattern)
    if normalized_pattern == "*":
        return True
    pattern_calls = parse_call_sequence(normalized_pattern)
    target = auction.calls
    return any(_expanded_pattern_calls(pattern_calls, seat_position) == target for seat_position in _seat_positions(seat_positions))


def historical_pattern_for(calls: tuple[str, ...], index: int) -> str:
    return compact_call_sequence(calls[:index])


def _seat_positions(seat_positions: list[int] | tuple[int, ...] | None) -> tuple[int | None, ...]:
    if seat_positions is None:
        return (None,)
    return tuple(seat_positions)


def _expanded_pattern_calls(pattern_calls: tuple[str, ...], seat_position: int | None) -> tuple[str, ...]:
    if seat_position is None:
        return pattern_calls
    return (*SEAT_POSITION_PASSES[seat_position], *pattern_calls)

