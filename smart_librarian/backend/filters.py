# Filtru limbaj nepotrivit
import os
from typing import Tuple, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Config din .env
STRICT = os.getenv("MODERATION_STRICT", "true").lower() == "true"
BLOCK_CATS = {
    c.strip().lower()
    for c in os.getenv("MODERATION_BLOCK_CATEGORIES", "").split(",")
    if c.strip()
}
# control separat pentru profanitate via LLM-classifier
PROFANITY_BLOCK = os.getenv("PROFANITY_BLOCK", "true").lower() == "true"

SAFE_RESPONSE = (
    "Îți mulțumesc! Din motive de siguranță, nu pot procesa întrebarea exact așa cum a fost formulată. "
    "Te rog reformulează fără termeni ofensatori sau conținut nepotrivit. "
    "Exemplu: «Te rog recomandă-mi o carte despre prietenie și curaj.»"
)

def _to_dict(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "model_dump"):   # Pydantic v2
        return obj.model_dump()
    if hasattr(obj, "dict"):         # Pydantic v1
        return obj.dict()
    out = {}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            val = getattr(obj, name)
        except Exception:
            continue
        if isinstance(val, (bool, int, float, str)) or val is None:
            out[name] = val
    return out

def _moderation_block(text: str) -> Tuple[bool, Dict[str, Any]]:
    resp = client.moderations.create(
        model="omni-moderation-latest",
        input=text
    )
    r = resp.results[0]
    flagged = bool(getattr(r, "flagged", False))
    cats = getattr(r, "categories", None)
    cats_dict: Dict[str, Any] = _to_dict(cats) if cats is not None else {}

    if STRICT and flagged:
        return True, {"results": [_to_dict(r)]}

    if not STRICT and BLOCK_CATS and cats_dict:
        for cat_name, is_true in cats_dict.items():
            base = cat_name.split("/")[0].lower()
            if bool(is_true) and base in BLOCK_CATS:
                return True, {"results": [_to_dict(r)]}

    return False, {"results": [_to_dict(r)]}

def _profanity_block_via_llm(text: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Clasificator LLM minim: răspunde STRICT doar cu ALLOW sau BLOCK.
    Blocăm dacă detectează injurii/profanitate/vulgaritate clară.
    """
    if not PROFANITY_BLOCK:
        return False, {"skipped": True}

    system = (
        "You are a strict profanity detector for user queries to a book-recommendation assistant. "
        "If the text contains clear profanity, slurs, or vulgar language (any language), respond exactly 'BLOCK'. "
        "If it is acceptable (even if critical but not profane), respond exactly 'ALLOW'. "
        "No explanation. Only one token: ALLOW or BLOCK."
    )
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text}
        ],
        temperature=0,
        max_tokens=3
    )
    verdict = (completion.choices[0].message.content or "").strip().upper()
    return (verdict == "BLOCK"), {"verdict": verdict}

def moderate_text(text: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Returnează:
      - blocked (bool)
      - message (str) pentru UI
      - raw (dict) cu detalii
    """
    blocked_mod, raw_mod = _moderation_block(text)
    if blocked_mod:
        return True, SAFE_RESPONSE, {"moderation": raw_mod, "profanity": None}

    blocked_prof, raw_prof = _profanity_block_via_llm(text)
    if blocked_prof:
        return True, SAFE_RESPONSE, {"moderation": raw_mod, "profanity": raw_prof}

    return False, "", {"moderation": raw_mod, "profanity": raw_prof}
