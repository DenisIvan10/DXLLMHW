# Interfață CLI
import sys
from pathlib import Path

# asigură-te că rădăcina proiectului este în sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.filters import moderate_text
from backend.openai_chat import recommend_with_summary
from extras.text_to_speech import synthesize_to_mp3
from extras.speech_to_text import transcribe_audio


def ask_text() -> str | None:
    """Cere întrebarea ca text (clasic)."""
    q = input("\nÎntrebare (sau 'exit'): ").strip()
    if q.lower() in {"exit", "quit"}:
        return None
    return q


def ask_voice() -> str | None:
    """Transcrie un fișier audio și întoarce textul ca întrebare."""
    path = input("\nCalea fișierului audio (wav/mp3/m4a/webm) sau 'back': ").strip()
    if path.lower() in {"back", "exit", "quit"}:
        return None
    try:
        q = transcribe_audio(path)
        print(f"[STT] Transcriere: {q}")
        return q
    except Exception as e:
        print(f"[STT] Eroare: {e}")
        return None


def main():
    print("=== Smart Librarian (CLI) — text / voice ===")
    print("Comenzi: t = text, v = voice din fișier, exit = ieșire")

    try:
        while True:
            mode = input("\nAlegi mod (t/v/exit): ").strip().lower()
            if mode in {"exit", "quit"}:
                break

            if mode == "v":
                q = ask_voice()
                if not q:
                    continue
            elif mode == "t":
                q = ask_text()
                if not q:
                    break
            else:
                print("Opțiune necunoscută. Alege 't' (text) sau 'v' (voice).")
                continue

            # Moderation (pasul 5)
            blocked, msg, _raw = moderate_text(q)
            if blocked:
                print("\n[Moderation] " + msg)
                continue

            # RAG + GPT + Tool (pasul 3-4)
            out = recommend_with_summary(q)
            print("\n=== Recomandare ===")
            print(out["answer"])

            # TTS (pasul 6)
            want_tts = input("\nGenerezi MP3 pentru acest răspuns? (y/n): ").strip().lower()
            if want_tts == "y":
                out_dir = ROOT / "outputs" / "audio"
                out_dir.mkdir(parents=True, exist_ok=True)
                out_file = out_dir / "recommendation.mp3"
                try:
                    path = synthesize_to_mp3(out["answer"], str(out_file))
                    print(f"[OK] MP3 salvat la: {path}")
                except Exception as e:
                    print(f"[TTS] Eroare: {e}")

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
