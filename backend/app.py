from __future__ import annotations

import json
from pathlib import Path

from engine.auction import Auction
from engine.cards import Hand
from engine.explanation import explain
from engine.loader import load_system
from engine.selector import choose_bid


def bid(request: dict) -> dict:
    system_id = request["system"]["id"]
    environment = request.get("environment", {})
    dealer = environment.get("dealer", "n")
    vulnerability = environment.get("vulnerability", "none")
    rules = load_system(system_id, Path(__file__).resolve().parent)
    auction = Auction.parse(request["auction"], dealer=dealer, vulnerability=vulnerability)
    hand = Hand.parse(request["hand"])
    selection = choose_bid(rules, auction, hand, environment)
    return explain(selection)


if __name__ == "__main__":
    sample = {
        "system": {"id": "expert_2over1"},
        "seat": "n",
        "auction": "1NP2DP",
        "hand": "SAQ74HKJ83DA62CQ5",
        "environment": {"dealer": "n", "vulnerability": "none", "scoring": "IMP"},
    }
    print(json.dumps(bid(sample), indent=2))
