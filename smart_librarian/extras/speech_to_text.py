# Speech to text
import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_STT_MODEL = os.getenv("STT_MODEL", "gpt-4o-mini-transcribe")

def transcribe_audio(file_path: str, model: Optional[str] = None) -> str:
    """
    Transcrie fișier audio (wav/mp3/m4a/webm...) și întoarce textul.
    """
    model = model or DEFAULT_STT_MODEL
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Nu găsesc fișierul audio: {file_path}")

    with open(file_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model=model,
            file=f,               # detectează automat tipul
            # language="ro",     # poți fixa limba; altfel auto-detect
            response_format="json"
        )
    # SDK v1: resp.text conține transcrierea
    return resp.text.strip()
