from pathlib import Path
import json
import unittest

import yaml

from engine.auction import Auction
from engine.cards import Hand
from engine.explanation import explain
from engine.loader import load_system
from engine.matcher import matches_context
from engine.selector import choose_bid


BACKEND_DIR = Path(__file__).resolve().parents[1]
CASES_DIR = Path(__file__).resolve().parent / "cases"


def _read_cases(file_name: str) -> list[dict]:
    return _read_yaml(file_name).get("cases", [])


def _read_yaml(file_name: str) -> dict:
    return yaml.safe_load((CASES_DIR / file_name).read_text(encoding="utf-8")) or {}


class FixtureBiddingTests(unittest.TestCase):
    def test_bidding_cases(self):
        for case in _read_cases("bidding.yaml"):
            with self.subTest(case=case["name"]):
                result = self._run_bidding_case(case)
                self._assert_bidding_expectations(result, case.get("expected", {}))

    def _run_bidding_case(self, case: dict) -> dict:
        environment = case.get("environment", {})
        rules = load_system(case["system"], BACKEND_DIR)
        auction = Auction.parse(
            case.get("auction", []),
            dealer=environment.get("dealer", "n"),
            vulnerability=environment.get("vulnerability", "none"),
        )
        hand = Hand.parse(case["hand"])
        return explain(choose_bid(rules, auction, hand, environment))

    def _assert_bidding_expectations(self, result: dict, expected: dict) -> None:
        if "call" in expected:
            self.assertEqual(result["call"], expected["call"])

        origin = expected.get("origin", {})
        actual_origin = result["public_meaning"]["origin"] if result["public_meaning"] else {}
        for key, value in origin.items():
            self.assertEqual(actual_origin.get(key), value)

        public_meaning = expected.get("public_meaning", {})
        actual_meaning = result["public_meaning"]["meaning"] if result["public_meaning"] else {}
        for key, value in public_meaning.items():
            self.assertEqual(actual_meaning.get(key), value)

        if "compared_candidate_calls" in expected:
            self.assertEqual(
                [candidate["call"] for candidate in result["internal_origin"]["compared_candidates"]],
                expected["compared_candidate_calls"],
            )

        if "selected_algorithm" in expected:
            self.assertEqual(result["internal_origin"]["selected"]["algorithm"], expected["selected_algorithm"])

        if "diagnostics" in expected:
            self.assertEqual(result["diagnostics"], expected["diagnostics"])

        for text in expected.get("diagnostics_include", []):
            self.assertTrue(any(text in diagnostic for diagnostic in result["diagnostics"]), result["diagnostics"])

        if "semantic_fact_types" in expected:
            self.assertEqual(
                [fact["fact_type"] for fact in result["internal_origin"]["semantic_facts"]],
                expected["semantic_fact_types"],
            )

        for index, fact_origin in enumerate(expected.get("semantic_fact_origins", [])):
            actual = result["internal_origin"]["semantic_facts"][index]["origin"]
            for key, value in fact_origin.items():
                self.assertEqual(actual.get(key), value)

        selected_criteria = {
            item["criterion_id"]
            for item in result["internal_origin"]["selected"].get("criteria_results", [])
        }
        for criterion_id in expected.get("selected_criteria_include", []):
            self.assertIn(criterion_id, selected_criteria)


class FixtureMatcherTests(unittest.TestCase):
    def test_matcher_cases(self):
        for case in _read_cases("matcher.yaml"):
            with self.subTest(case=case["name"]):
                for calls in case.get("matches", []):
                    self.assertTrue(matches_context(case["context"], Auction.parse(calls)), calls)
                for calls in case.get("rejects", []):
                    self.assertFalse(matches_context(case["context"], Auction.parse(calls)), calls)


class FixtureHandParserTests(unittest.TestCase):
    def test_valid_hand_cases(self):
        for case in _read_yaml("hands.yaml").get("valid", []):
            with self.subTest(case=case["name"]):
                hand = Hand.parse(case["hand"])
                expected = case.get("expected", {})
                for suit in ("spades", "hearts", "diamonds", "clubs"):
                    if suit in expected:
                        self.assertEqual(getattr(hand, suit), expected[suit])
                if "hcp" in expected:
                    self.assertEqual(hand.hcp, expected["hcp"])

    def test_invalid_hand_cases(self):
        for case in _read_yaml("hands.yaml").get("invalid", []):
            with self.subTest(case=case["name"]):
                with self.assertRaisesRegex((ValueError, TypeError), case["error_contains"]):
                    Hand.parse(case["hand"])


class InfrastructureTests(unittest.TestCase):
    def test_auction_calls_are_canonicalized(self):
        auction = Auction.parse("1NT pass 2d", dealer="N", vulnerability="NONE")

        self.assertEqual(auction.calls, ("1N", "P", "2D"))
        self.assertEqual(auction.canonical_key(), "dealer=n;vul=none;calls=1NP2D")

    def test_compact_auction_allows_arbitrary_spaces(self):
        auction = Auction.parse(" 1N   P 1S P X R ")

        self.assertEqual(auction.calls, ("1N", "P", "1S", "P", "X", "R"))
        self.assertEqual(auction.compact_sequence(), "1NP1SPXR")

    def test_loader_accepts_json_compatible_yaml(self):
        scratch = BACKEND_DIR / "tmp_json_compat"
        systems_dir = scratch / "systems"
        gadgets_dir = scratch / "gadgets" / "nt"
        systems_dir.mkdir(parents=True, exist_ok=True)
        gadgets_dir.mkdir(parents=True, exist_ok=True)
        try:
            (systems_dir / "json_style.yaml").write_text(
                json.dumps({"id": "json_style", "name": "JSON Style", "gadgets": ["nt.simple"]}),
                encoding="utf-8",
            )
            (gadgets_dir / "simple.yaml").write_text(
                json.dumps(
                    {
                        "id": "simple",
                        "namespace": "nt",
                        "name": "Simple JSON-Compatible Gadget",
                        "version": "0.1.0",
                        "author": {"name": "Partner Prototype"},
                        "rules": [
                            {
                                "id": "meaning_open_1N",
                                "type": "meaning",
                                "auction_pattern": "",
                                "call": "1N",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            rules = load_system("json_style", scratch)

            self.assertEqual(len(rules), 1)
            self.assertEqual(rules[0].qualified_rule_id, "nt/simple@0.1.0:meaning_open_1N")
        finally:
            for path in sorted(scratch.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()


if __name__ == "__main__":
    unittest.main()
