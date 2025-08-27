# Generare imagine cu AI
import os, base64
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Notă: pentru generare imagine, în SDK v1 se folosește images.generate cu modelul "gpt-image-1".
# Returnăm calea PNG-ului salvat pe disc.
def generate_book_image(
    title: str,
    style_hint: str = "watercolor poster",
    extra_prompt: Optional[str] = None,
    out_path: str = "outputs/images/recommendation.png",
    size: str = "1024x1024",
) -> str:
    assert title and title.strip(), "Lipsește titlul pentru generarea imaginii."
    prompt = (
        f"Create a single, tasteful cover-style illustration representing the book '{title}'. "
        f"Style: {style_hint}. Avoid text overlays and copyrighted logos. Focus on themes and mood."
    )
    if extra_prompt and extra_prompt.strip():
        prompt += f" Extra details: {extra_prompt.strip()}"

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size
    )
    b64 = result.data[0].b64_json
    img_bytes = base64.b64decode(b64)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        f.write(img_bytes)
    return str(out)
