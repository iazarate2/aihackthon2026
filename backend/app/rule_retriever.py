"""Lightweight rule retrieval for basketball charge/block reviews."""

import re

from app.rules_engine import get_rules

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "before", "by", "for",
    "from", "if", "in", "into", "is", "it", "of", "on", "or", "the",
    "their", "this", "to", "when", "with",
}

_DOMAIN_TERMS = {
    "airborne": {"air", "airborne", "jump", "jumping", "left ground", "upward", "gather"},
    "blocking": {"block", "blocking", "slide", "sliding", "lateral", "moving", "hip", "shoulder"},
    "charge": {"charge", "set", "stationary", "torso", "chest", "square", "feet"},
    "contact": {"contact", "body", "torso", "chest", "hip", "shoulder", "arm"},
    "restricted": {"restricted", "arc", "semicircle", "basket", "rim", "paint"},
    "inconclusive": {"blur", "blocked", "obscured", "angle", "quality", "unclear", "cannot"},
}

_SEVERE_INCONCLUSIVE_TERMS = {
    "no players",
    "does not show",
    "not show",
    "not visible",
    "cannot see",
    "off screen",
    "blocked from view",
    "camera cut",
    "crowd shot",
    "timeout",
    "bench",
    "not captured",
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {word for word in words if len(word) > 2 and word not in _STOPWORDS}


def _rule_text(rule: dict) -> str:
    parts = [rule.get("title", ""), rule.get("summary", "")]
    for key, value in rule.items():
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
    return " ".join(parts)


def _domain_bonus(query: str, rule_key: str) -> int:
    query_lower = query.lower()
    bonus = 0
    if rule_key == "legal_guarding_position":
        bonus += sum(2 for term in _DOMAIN_TERMS["charge"] if term in query_lower)
    if rule_key == "defender_moving_into_path":
        bonus += sum(2 for term in _DOMAIN_TERMS["blocking"] if term in query_lower)
    if rule_key == "airborne_offensive_player":
        bonus += sum(2 for term in _DOMAIN_TERMS["airborne"] if term in query_lower)
    if rule_key == "contact_location":
        bonus += sum(2 for term in _DOMAIN_TERMS["contact"] if term in query_lower)
    if rule_key == "restricted_area":
        bonus += sum(2 for term in _DOMAIN_TERMS["restricted"] if term in query_lower)
    if rule_key == "inconclusive_evidence":
        bonus += sum(2 for term in _DOMAIN_TERMS["inconclusive"] if term in query_lower)
    return bonus


def retrieve_rules(query: str, top_k: int = 3) -> list[dict]:
    """Return the most relevant rule chunks for a play description."""
    rules = get_rules()
    query_terms = _tokenize(query)
    query_lower = query.lower()
    severe_inconclusive = any(term in query_lower for term in _SEVERE_INCONCLUSIVE_TERMS)
    scored = []

    for key, rule in rules.items():
        rule_terms = _tokenize(_rule_text(rule))
        overlap = len(query_terms & rule_terms)
        score = overlap + _domain_bonus(query, key)
        if key == "inconclusive_evidence" and not severe_inconclusive:
            score -= 5
        if key == "inconclusive_evidence" and severe_inconclusive:
            score += 5
        scored.append((score, key, rule))

    scored.sort(key=lambda item: item[0], reverse=True)

    retrieved = []
    for score, key, rule in scored[:top_k]:
        retrieved.append({
            "id": key,
            "title": rule["title"],
            "summary": rule["summary"],
            "source_label": rule.get("source_label"),
            "source_url": rule.get("source_url"),
            "video_rulebook_url": rule.get("video_rulebook_url"),
            "score": score,
        })
    return retrieved


def format_retrieved_rules(rules: list[dict]) -> str:
    """Format retrieved rule chunks for the final reasoning prompt."""
    lines = []
    for idx, rule in enumerate(rules, start=1):
        lines.append(f"{idx}. [{rule['id']}] {rule['title']}")
        if rule.get("source_label"):
            lines.append(f"Official source: {rule['source_label']}")
        lines.append(rule["summary"])
        lines.append("")
    return "\n".join(lines).strip()
