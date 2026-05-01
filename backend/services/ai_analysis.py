"""
AI Analysis Service
Analyzes extracted soccer frames against IFAB rules.

Supports two modes controlled by the MOCK_AI environment variable:
  MOCK_AI=true  → returns realistic fake results (no API cost)
  MOCK_AI=false → calls a real multimodal AI API
"""

import os
import json
import base64
import random
import asyncio

from dotenv import load_dotenv
from openai import AsyncOpenAI

from services.rulebook import get_rules_context

load_dotenv()

MOCK_AI = os.getenv("MOCK_AI", "true").lower() == "true"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def analyze_frames(video_id: str, frame_paths: list[str]) -> dict:
    """
    Analyze extracted frames and return a structured verdict.

    Args:
        video_id:     Unique identifier for the video.
        frame_paths:  List of frame image file paths on disk.

    Returns:
        Dict with verdict, confidence, rule_reference, explanation,
        and key_observations.
    """
    if MOCK_AI:
        return await _mock_analysis(video_id, frame_paths)
    else:
        return await _real_analysis(video_id, frame_paths)


# ---------------------------------------------------------------------------
# Mock AI (for development / demo without API costs)
# ---------------------------------------------------------------------------

# A pool of realistic mock responses to rotate through
_MOCK_SCENARIOS = [
    {
        "verdict": "Foul",
        "confidence": 0.84,
        "rule_reference": "Law 12 - Careless Tackle",
        "explanation": (
            "The defender appears to make contact with the attacker's "
            "planted leg before winning the ball. The challenge is deemed "
            "careless as it trips the opponent without a reasonable attempt "
            "to play the ball first."
        ),
        "key_frame": 6,
        "key_frame_reason": "Moment of contact between defender's foot and attacker's planted leg",
        "key_observations": [
            "Defender lunges toward attacker's lower leg",
            "Ball changes direction after contact, not before",
            "Attacker loses balance immediately upon impact",
        ],
    },
    {
        "verdict": "Fair Call",
        "confidence": 0.78,
        "rule_reference": "Law 12 - Fair Challenge",
        "explanation": (
            "The defender makes a clean sliding tackle, clearly contacting "
            "the ball first. Any subsequent contact with the attacker appears "
            "incidental and unavoidable."
        ),
        "key_frame": 5,
        "key_frame_reason": "Defender's foot clearly makes contact with the ball before reaching the attacker",
        "key_observations": [
            "Defender's foot reaches the ball before the attacker",
            "Slide is controlled and not excessively forceful",
            "Attacker stumbles but contact was after ball was played",
        ],
    },
    {
        "verdict": "Dangerous Play",
        "confidence": 0.91,
        "rule_reference": "Law 12 - Red Card (Sending Off)",
        "explanation": (
            "The defender's challenge uses excessive force with studs raised "
            "at knee height. This endangers the safety of the opponent and "
            "constitutes serious foul play regardless of whether the ball "
            "was won."
        ),
        "key_frame": 7,
        "key_frame_reason": "Studs visibly raised at knee height during the challenge",
        "key_observations": [
            "Studs are raised above ankle height during the challenge",
            "Defender leaves the ground with both feet",
            "High speed and force of the tackle pose clear danger",
        ],
    },
    {
        "verdict": "Inconclusive",
        "confidence": 0.45,
        "rule_reference": "Law 12 - Inconclusive Evidence",
        "explanation": (
            "The camera angle and frame quality do not provide sufficient "
            "visual evidence to determine whether the defender contacted "
            "the ball or the opponent first."
        ),
        "key_frame": 8,
        "key_frame_reason": "Closest frame to the moment of contact, but view is obstructed",
        "key_observations": [
            "Key moment of contact is partially obscured",
            "Low frame rate makes sequencing difficult",
            "Multiple players block the camera's line of sight",
        ],
    },
    {
        "verdict": "Foul",
        "confidence": 0.72,
        "rule_reference": "Law 12 - Tripping",
        "explanation": (
            "The defender extends their leg into the attacker's path without "
            "making a play on the ball, causing the attacker to trip and fall."
        ),
        "key_frame": 4,
        "key_frame_reason": "Defender's extended leg makes contact with the attacker's ankle",
        "key_observations": [
            "Defender's leg is extended across the attacker's running line",
            "No visible attempt to play the ball",
            "Attacker was in a promising attacking position",
        ],
    },
]


async def _mock_analysis(video_id: str, frame_paths: list[str]) -> dict:
    """Return a realistic mock analysis after simulating AI latency."""
    # Simulate API processing time (1–3 seconds)
    await asyncio.sleep(random.uniform(1.0, 3.0))

    scenario = random.choice(_MOCK_SCENARIOS)
    # Add slight randomness to confidence so repeated calls look natural
    result = {**scenario}
    result["confidence"] = round(
        max(0.1, min(1.0, result["confidence"] + random.uniform(-0.05, 0.05))),
        2,
    )
    # Randomize key_frame based on actual number of frames
    max_frame = max(len(frame_paths), 1)
    result["key_frame"] = random.randint(1, max_frame)
    return result


# ---------------------------------------------------------------------------
# Real AI — OpenAI GPT-4o Vision
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are an expert soccer/football referee with 20 years of experience analyzing tackles and challenges using video replay (VAR).

You will receive a sequence of numbered frames extracted from a short soccer clip showing a tackle or challenge. The frames are in CHRONOLOGICAL ORDER — Frame 1 is the earliest, Frame N is the latest.

=== ANALYSIS PROCEDURE (follow these steps in order) ===

STEP 1 — IDENTIFY THE PLAYERS:
- Which player is the defender (the one making the challenge/tackle)?
- Which player is the attacker (the one with or going for the ball)?
- Where is the ball in each frame?

STEP 2 — TRACK THE SEQUENCE OF EVENTS:
- In which frame does the defender BEGIN the challenge?
- In which frame does FIRST CONTACT occur (defender touching ball OR opponent)?
- What does the defender contact FIRST — the ball or the opponent?
- What happens AFTER contact — does the attacker fall, lose the ball, continue?

STEP 3 — EVALUATE THE CHALLENGE using this decision tree:

A) Did the defender clearly play the ball FIRST with no careless contact?
   → YES → "Fair Call"

B) Did the defender contact the opponent BEFORE or WITHOUT playing the ball?
   → Was it careless (lack of attention/consideration)?
     → YES → "Foul" (direct free kick)
   → Was it reckless (disregard for danger to opponent)?
     → YES → "Foul" + note yellow card potential
   → Was it with excessive force (far exceeding necessary force, endangering safety)?
     → YES → "Dangerous Play" + note red card potential

C) Does the defender trip, kick, push, charge, or strike the opponent?
   → YES → "Foul" or "Dangerous Play" depending on force

D) Is the visual evidence too unclear, obstructed, or ambiguous to determine what happened?
   → YES → "Inconclusive"

STEP 4 — DETERMINE THE KEY FRAME:
- Which single frame most clearly shows the decisive moment (first contact, ball contact, or the dangerous action)?

=== OUTPUT FORMAT ===

Return ONLY valid JSON:
{
  "verdict": "Fair Call | Foul | Dangerous Play | Inconclusive",
  "confidence": 0.0,
  "rule_reference": "Law 12 - short rule name",
  "explanation": "2-3 sentence explanation covering: what the defender did, what contact occurred, and why this matches the rule",
  "key_frame": 1,
  "key_frame_reason": "what is visible in this specific frame and how it confirms the verdict under the cited rule",
  "key_observations": [
    "observation about defender's body position or movement",
    "observation about point and timing of contact",
    "observation about ball position relative to contact",
    "observation about result/effect on attacker"
  ]
}

RULES:
- "verdict" must be EXACTLY one of: Fair Call, Foul, Dangerous Play, Inconclusive
- "confidence" must be 0.0–1.0 (use 0.3–0.5 if evidence is borderline, 0.7+ if clear)
- "key_frame" is 1-based (Frame 1, Frame 2, etc.)
- Provide 3–5 key_observations
- Do NOT return markdown fences — return ONLY the raw JSON object"""


def _encode_frame(path: str) -> str:
    """Read an image file and return its base64-encoded string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def _real_analysis(video_id: str, frame_paths: list[str]) -> dict:
    """
    Send extracted frames to OpenAI GPT-4o for multimodal analysis.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not set in backend/.env. "
            "Set MOCK_AI=true or add your API key."
        )

    client = AsyncOpenAI(api_key=api_key)

    # Build the message content: rules context + all frames as images
    rules_context = get_rules_context()

    content: list[dict] = [
        {
            "type": "text",
            "text": (
                f"Analyze the following {len(frame_paths)} frames extracted "
                f"from a soccer clip. Use the rules below to inform your decision.\n\n"
                f"{rules_context}"
            ),
        },
    ]

    # Attach each frame with a text label so the AI can track temporal order
    for idx, path in enumerate(frame_paths, start=1):
        content.append({
            "type": "text",
            "text": f"--- Frame {idx} of {len(frame_paths)} ---",
        })
        b64 = _encode_frame(path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{b64}",
                "detail": "high",
            },
        })

    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        max_tokens=800,  # more room for structured reasoning
        temperature=0.2,  # lower temp for more consistent decisions
    )

    raw = response.choices[0].message.content or ""

    # Strip markdown fences if the model wraps the JSON
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]  # remove opening fence line
    if raw.endswith("```"):
        raw = raw.rsplit("\n", 1)[0]  # remove closing fence line
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # If the model returns something unparseable, return Inconclusive
        result = {
            "verdict": "Inconclusive",
            "confidence": 0.3,
            "rule_reference": "Law 12 - Inconclusive Evidence",
            "explanation": "AI response could not be parsed into a structured verdict.",
            "key_observations": ["Raw AI output was not valid JSON"],
        }

    # Validate and clamp confidence
    result["confidence"] = round(
        max(0.0, min(1.0, float(result.get("confidence", 0.5)))), 2
    )

    # Validate key_frame is within bounds
    key_frame = result.get("key_frame", 1)
    try:
        key_frame = int(key_frame)
    except (TypeError, ValueError):
        key_frame = 1
    result["key_frame"] = max(1, min(key_frame, len(frame_paths)))

    return result
