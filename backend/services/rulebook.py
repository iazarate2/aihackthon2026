"""
Rulebook Service
Simplified IFAB Law 12 rules used as context for AI analysis.
"""

# Each rule is a dict with a short name and the rule text.
# These get injected into the AI prompt so it can reference them.
LAWS = [
    {
        "id": "law12-trip",
        "name": "Law 12 - Tripping",
        "text": (
            "A direct free kick is awarded if a player trips or attempts "
            "to trip an opponent."
        ),
    },
    {
        "id": "law12-kick",
        "name": "Law 12 - Kicking",
        "text": (
            "A direct free kick is awarded if a player kicks or attempts "
            "to kick an opponent."
        ),
    },
    {
        "id": "law12-tackle",
        "name": "Law 12 - Careless Tackle",
        "text": (
            "A direct free kick is awarded if a player tackles or challenges "
            "an opponent carelessly, recklessly, or with excessive force."
        ),
    },
    {
        "id": "law12-push",
        "name": "Law 12 - Pushing",
        "text": (
            "A direct free kick is awarded if a player pushes an opponent."
        ),
    },
    {
        "id": "law12-charge",
        "name": "Law 12 - Charging",
        "text": (
            "A direct free kick is awarded if a player charges an opponent "
            "in a careless, reckless, or excessively forceful manner."
        ),
    },
    {
        "id": "law12-yellow",
        "name": "Law 12 - Yellow Card (Caution)",
        "text": (
            "A player is cautioned (yellow card) if they commit a reckless "
            "challenge — one that disregards danger to the opponent."
        ),
    },
    {
        "id": "law12-red",
        "name": "Law 12 - Red Card (Sending Off)",
        "text": (
            "A player is sent off (red card) for serious foul play — a tackle "
            "or challenge using excessive force that endangers the safety "
            "of the opponent."
        ),
    },
    {
        "id": "law12-fair",
        "name": "Law 12 - Fair Challenge",
        "text": (
            "If the defender clearly plays the ball before making incidental "
            "contact with the opponent, the challenge may be considered fair."
        ),
    },
    {
        "id": "law12-inconclusive",
        "name": "Law 12 - Inconclusive Evidence",
        "text": (
            "If the visual evidence is unclear or insufficient to determine "
            "the nature of the challenge, the decision should be Inconclusive."
        ),
    },
]


def get_rules_context() -> str:
    """
    Return all rules formatted as a text block for injection into an AI prompt.
    """
    lines = ["=== Simplified IFAB Law 12 Rules ===\n"]
    for rule in LAWS:
        lines.append(f"[{rule['name']}]")
        lines.append(f"{rule['text']}\n")
    return "\n".join(lines)
