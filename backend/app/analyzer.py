"""
Analyzer — produces a review verdict for charge vs. block plays.

Supports two modes:
  MOCK_AI=true  → random mock responses (no API cost)
  MOCK_AI=false → real GPT-4o vision analysis
"""

import os
import json
import base64
import hashlib
import random
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from app.rules_engine import get_rule
from app.rule_retriever import format_retrieved_rules, retrieve_rules

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BACKEND_DIR)

load_dotenv(os.path.join(BACKEND_DIR, ".env"))
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

MOCK_AI = os.getenv("MOCK_AI", "true").lower() == "true"


# ---------------------------------------------------------------------------
# Verdict logic (shared by both sample-case and video-upload paths)
# ---------------------------------------------------------------------------

def compute_verdict(
    original_call: str,
    predicted_call: str,
    confidence: float,
) -> tuple[str, str]:
    """
    Apply the hackathon verdict/recommendation logic.

    Returns (verdict, challenge_recommendation).
    """
    if predicted_call == "Inconclusive":
        return "Inconclusive", "Stands as Called"

    if confidence < 0.55:
        return "Inconclusive", "Stands as Called"

    if original_call == predicted_call:
        return "Fair Call", "Uphold Call"

    if confidence >= 0.70:
        return "Bad Call", "Overturn Call"

    return "Inconclusive", "Stands as Called"


# ---------------------------------------------------------------------------
# Sample-case analysis (no video needed)
# ---------------------------------------------------------------------------

def analyze_sample_case(case: dict, original_call: str) -> dict:
    """Build a full review response from a pre-defined sample case."""
    predicted = case["predicted_call"]
    conf = case["confidence"]
    verdict, rec = compute_verdict(original_call, predicted, conf)

    rule = get_rule(case["rule_key"])

    return {
        "verdict": verdict,
        "challenge_recommendation": rec,
        "confidence": conf,
        "original_call": original_call,
        "predicted_call": predicted,
        "review_type": "Charge vs. Block",
        "evidence": case["evidence"],
        "rule_reference": {
            "title": rule["title"],
            "summary": rule["summary"],
            "source_label": rule.get("source_label"),
            "source_url": rule.get("source_url"),
            "video_rulebook_url": rule.get("video_rulebook_url"),
        },
        "key_frames": [],  # sample cases have no real frames
        "limitations": case["limitations"],
    }


# ---------------------------------------------------------------------------
# Mock video analysis (for user-uploaded clips)
# ---------------------------------------------------------------------------

_MOCK_PREDICTIONS = [
    {
        "predicted_call": "Charge",
        "confidence": 0.79,
        "evidence": [
            "Defender appears to have both feet set before contact.",
            "Contact occurs through the defender's chest/torso area.",
            "Offensive player drives forward into the set defender.",
            "Defender is positioned outside the restricted area.",
        ],
        "rule_key": "legal_guarding_position",
        "limitations": [
            "Frame rate may miss the exact moment feet were planted.",
        ],
    },
    {
        "predicted_call": "Blocking Foul",
        "confidence": 0.76,
        "evidence": [
            "Defender appears to still be sliding laterally at contact.",
            "Contact is initiated by the defender's hip area.",
            "Offensive player was driving in a straight line to the basket.",
            "Defender's feet are not fully set at the moment of impact.",
        ],
        "rule_key": "defender_moving_into_path",
        "limitations": [
            "Lower body partially obscured — foot position is estimated.",
        ],
    },
    {
        "predicted_call": "Charge",
        "confidence": 0.62,
        "evidence": [
            "Defender appears mostly set but there is slight movement.",
            "Contact occurs through the torso area.",
            "Offensive player gathers and drives into the defender.",
            "Restricted area line is not fully visible.",
        ],
        "rule_key": "legal_guarding_position",
        "limitations": [
            "Borderline positioning — confidence reduced.",
            "Restricted area visibility is limited.",
        ],
    },
    {
        "predicted_call": "Blocking Foul",
        "confidence": 0.83,
        "evidence": [
            "Offensive player is already airborne before defender sets.",
            "Defender slides under the airborne player.",
            "Contact occurs after the offensive player has left the ground.",
            "Defender was still moving into position.",
        ],
        "rule_key": "airborne_offensive_player",
        "limitations": [
            "Exact timing of the gather step is difficult to determine.",
        ],
    },
    {
        "predicted_call": "Inconclusive",
        "confidence": 0.38,
        "evidence": [
            "Camera angle does not clearly show the defender's feet.",
            "Moment of contact is partially blocked by another player.",
            "Cannot determine if defender was legally set.",
            "Video quality makes positioning assessment unreliable.",
        ],
        "rule_key": "inconclusive_evidence",
        "limitations": [
            "Poor camera angle — lower body not visible.",
            "Key contact frame may be missing.",
        ],
    },
]


def analyze_video_upload(
    original_call: str,
    frame_urls: list[str],
    frame_paths: Optional[list[str]] = None,
    filename: Optional[str] = None,
) -> dict:
    """
    Analyze uploaded video frames.
    Uses GPT-4o if MOCK_AI=false, otherwise deterministic mock based on filename.
    """
    if not MOCK_AI and frame_paths:
        return _real_analysis(original_call, frame_urls, frame_paths)

    # --- Deterministic mock: same filename always gets the same result ---
    key = filename or "default"
    index = int(hashlib.sha256(key.encode()).hexdigest(), 16) % len(_MOCK_PREDICTIONS)
    mock = _MOCK_PREDICTIONS[index]

    predicted = mock["predicted_call"]
    conf = mock["confidence"]  # fixed confidence — no random jitter

    verdict, rec = compute_verdict(original_call, predicted, conf)
    rule = get_rule(mock["rule_key"])

    return {
        "verdict": verdict,
        "challenge_recommendation": rec,
        "confidence": conf,
        "original_call": original_call,
        "predicted_call": predicted,
        "review_type": "Charge vs. Block",
        "evidence": mock["evidence"],
        "rule_reference": {
            "title": rule["title"],
            "summary": rule["summary"],
            "source_label": rule.get("source_label"),
            "source_url": rule.get("source_url"),
            "video_rulebook_url": rule.get("video_rulebook_url"),
        },
        "key_frames": frame_urls,
        "limitations": mock["limitations"],
    }


# ---------------------------------------------------------------------------
# Real GPT-4o Vision Analysis
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are an expert NBA/NCAA basketball referee with 20 years of experience reviewing charge vs. blocking foul calls using instant replay.

You will receive numbered frames from a basketball clip showing a charge/block play.

=== ANALYSIS PROCEDURE ===

STEP 1 — IDENTIFY:
- Who is the defender (taking the charge)?
- Who is the offensive player (driving/shooting)?
- Where is the ball?

STEP 2 — EVALUATE LEGAL GUARDING POSITION:
- Are the defender's feet set BEFORE contact?
- Is the defender facing the offensive player with torso square?
- Is the defender still sliding or moving laterally at contact?

STEP 3 — CHECK ADDITIONAL FACTORS:
- Is the offensive player already airborne before the defender sets?
- Where on the body does contact occur (torso = charge indicator, hip/shoulder = block indicator)?
- Is the defender inside or outside the restricted area?
- Is the visual evidence clear enough to make a determination?

STEP 4 — DECISION TREE:
A) Defender feet set + torso square + contact through chest BEFORE offensive player gathers → "Charge"
B) Defender still moving/sliding at contact → "Blocking Foul"
C) Offensive player airborne before defender sets → "Blocking Foul"
D) Minimal/incidental contact with no advantage → "No Call"
E) Cannot determine from frames → "Inconclusive"

=== RULES CONTEXT ===
{rules_context}

=== OUTPUT ===
Return ONLY valid JSON:
{{
  "predicted_call": "Charge | Blocking Foul | No Call | Inconclusive",
  "confidence": 0.0,
  "evidence": [
    "observation 1",
    "observation 2",
    "observation 3",
    "observation 4"
  ],
  "rule_key": "legal_guarding_position | defender_moving_into_path | airborne_offensive_player | contact_location | restricted_area | inconclusive_evidence",
  "limitations": [
    "limitation 1"
  ]
}}

RULES:
- "predicted_call" must be EXACTLY one of: Charge, Blocking Foul, No Call, Inconclusive
- "confidence" must be 0.0-1.0
- "rule_key" must match one of the rule IDs listed above
- Provide 3-5 evidence bullets describing what you see
- Do NOT return markdown fences — return ONLY the raw JSON object"""


def _encode_frame(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


_OBSERVATION_PROMPT = """You are analyzing frames from a basketball charge/block play.

Describe only what is visible. Do not decide the verdict yet.

Return ONLY valid JSON:
{{
  "play_description": "concise description of the sequence",
  "visual_cues": [
    "cue 1",
    "cue 2",
    "cue 3"
  ],
  "uncertainties": [
    "uncertainty 1"
  ]
}}"""


_FINAL_RAG_PROMPT = """You are an expert NBA/NCAA basketball referee reviewing a charge vs. blocking foul call.

Use ONLY the retrieved rule context below to decide whether the original call is fair.
If the frames or description do not provide enough evidence, return Inconclusive rather than guessing.

=== ORIGINAL CALL ===
{original_call}

=== AI PLAY DESCRIPTION ===
{play_description}

=== VISUAL CUES ===
{visual_cues}

=== UNCERTAINTIES ===
{uncertainties}

=== RETRIEVED RULE CONTEXT ===
{retrieved_rules}

=== DECISION CRITERIA ===
- If the retrieved rules support the original call, predicted_call should match the original call.
- If the retrieved rules clearly support the opposite call, predicted_call should be the better supported call.
- If evidence is unclear, predicted_call should be Inconclusive.

Return ONLY valid JSON:
{{
  "predicted_call": "Charge | Blocking Foul | No Call | Inconclusive",
  "confidence": 0.0,
  "evidence": [
    "observation tied to retrieved rule context",
    "observation tied to retrieved rule context",
    "observation tied to retrieved rule context"
  ],
  "rule_key": "legal_guarding_position | defender_moving_into_path | airborne_offensive_player | contact_location | restricted_area | inconclusive_evidence",
  "cited_rule_ids": [
    "rule_id_1",
    "rule_id_2"
  ],
  "limitations": [
    "limitation 1"
  ]
}}"""


def _json_from_response(raw: str, fallback: dict) -> dict:
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("\n", 1)[0]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return fallback


def _real_analysis(
    original_call: str,
    frame_urls: list[str],
    frame_paths: list[str],
) -> dict:
    """Analyze frames with a lightweight RAG flow over basketball rules."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Set MOCK_AI=true or add key.")

    client = OpenAI(api_key=api_key)

    content = [
        {
            "type": "text",
            "text": f"Describe these {len(frame_paths)} frames from a basketball charge/block play. The original referee call was: {original_call}.",
        }
    ]

    for idx, path in enumerate(frame_paths, start=1):
        content.append({"type": "text", "text": f"--- Frame {idx} of {len(frame_paths)} ---"})
        b64 = _encode_frame(path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"},
        })

    try:
        observation_response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": _OBSERVATION_PROMPT},
                {"role": "user", "content": content},
            ],
            max_tokens=650,
            temperature=0.2,
        )
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI analysis failed: {e}") from e

    observation = _json_from_response(
        observation_response.choices[0].message.content or "",
        {
            "play_description": "The play could not be described reliably from the AI response.",
            "visual_cues": [],
            "uncertainties": ["AI play-description response could not be parsed."],
        },
    )
    visual_cues = observation.get("visual_cues", [])
    uncertainties = observation.get("uncertainties", [])
    retrieval_query = " ".join([
        original_call,
        str(observation.get("play_description", "")),
        " ".join(str(cue) for cue in visual_cues),
        " ".join(str(item) for item in uncertainties),
    ])
    retrieved_rules = retrieve_rules(retrieval_query, top_k=3)
    retrieved_context = format_retrieved_rules(retrieved_rules)

    try:
        final_response = client.chat.completions.create(
            model=os.getenv("OPENAI_TEXT_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o")),
            messages=[
                {
                    "role": "system",
                    "content": _FINAL_RAG_PROMPT.format(
                        original_call=original_call,
                        play_description=observation.get("play_description", ""),
                        visual_cues=json.dumps(visual_cues),
                        uncertainties=json.dumps(uncertainties),
                        retrieved_rules=retrieved_context,
                    ),
                },
                {"role": "user", "content": "Return the final officiating review JSON."},
            ],
            max_tokens=800,
            temperature=0.2,
        )
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI RAG verdict failed: {e}") from e

    ai = _json_from_response(
        final_response.choices[0].message.content or "",
        {
            "predicted_call": "Inconclusive",
            "confidence": 0.3,
            "evidence": ["AI response could not be parsed."],
            "rule_key": "inconclusive_evidence",
            "cited_rule_ids": ["inconclusive_evidence"],
            "limitations": ["Response parsing failed."],
        },
    )

    predicted = ai.get("predicted_call", "Inconclusive")
    if predicted not in {"Charge", "Blocking Foul", "No Call", "Inconclusive"}:
        predicted = "Inconclusive"
    conf = round(max(0.0, min(1.0, float(ai.get("confidence", 0.5)))), 2)
    verdict, rec = compute_verdict(original_call, predicted, conf)
    rule = get_rule(ai.get("rule_key", "inconclusive_evidence"))
    cited_ids = set(ai.get("cited_rule_ids", []))
    cited_rules = [
        rule_item for rule_item in retrieved_rules
        if rule_item["id"] in cited_ids
    ] or retrieved_rules

    return {
        "verdict": verdict,
        "challenge_recommendation": rec,
        "confidence": conf,
        "original_call": original_call,
        "predicted_call": predicted,
        "review_type": "Charge vs. Block",
        "evidence": ai.get("evidence", []),
        "rule_reference": {
            "title": rule["title"],
            "summary": rule["summary"],
            "source_label": rule.get("source_label"),
            "source_url": rule.get("source_url"),
            "video_rulebook_url": rule.get("video_rulebook_url"),
        },
        "play_description": observation.get("play_description", ""),
        "retrieved_rules": retrieved_rules,
        "cited_rules": cited_rules,
        "key_frames": frame_urls,
        "limitations": ai.get("limitations", []),
    }
