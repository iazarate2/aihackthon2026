"""Basketball rules engine — loads rules and resolves references."""

import json
import os

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_json(name: str) -> dict:
    with open(os.path.join(_DATA_DIR, name)) as f:
        return json.load(f)


def get_rules() -> dict:
    """Return the full rules dict keyed by rule id."""
    return _load_json("basketball_rules.json")["rules"]


def get_rule(rule_key: str) -> dict:
    """Return a single rule by key, or a fallback."""
    rules = get_rules()
    return rules.get(rule_key, rules["inconclusive_evidence"])


def get_sample_cases() -> list[dict]:
    """Return all sample cases."""
    return _load_json("sample_cases.json")["cases"]


def get_sample_case(case_id: str) -> dict | None:
    """Return a single sample case by id, or None."""
    for case in get_sample_cases():
        if case["id"] == case_id:
            return case
    return None
