# Text to Speech
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
DEFAULT_TTS_VOICE = os.getenv("TTS_VOICE", "alloy")

def synthesize_to_mp3(
    text: str,
    out_path: str = "output.mp3",
    voice: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """
    Generează un fișier MP3 din text și returnează calea fișierului.
    """
    assert text and text.strip(), "Text gol pentru TTS."
    voice = voice or DEFAULT_TTS_VOICE
    model = model or DEFAULT_TTS_MODEL

    # Creează folderul de output dacă nu există
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Non-streaming: scriem direct conținutul în fișier
    resp = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text
    )
    with open(out_file, "wb") as f:
        f.write(resp.content)

    return str(out_file)
