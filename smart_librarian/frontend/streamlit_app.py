# Interfață Streamlit
import sys
from pathlib import Path

# Asigură-te că rădăcina proiectului e în sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from backend.filters import moderate_text
from backend.openai_chat import recommend_with_summary
from extras.text_to_speech import synthesize_to_mp3
from extras.speech_to_text import transcribe_audio
from extras.image_gen import generate_book_image

# Încercăm să importăm componenta de microfon din browser
try:
    from streamlit_mic_recorder import mic_recorder
    MIC_AVAILABLE = True
except Exception:
    MIC_AVAILABLE = False

st.set_page_config(page_title="Smart Librarian", page_icon="📚", layout="centered")
st.title("📚 Smart Librarian (RAG + GPT + Tool + TTS + STT + Image)")

# --- Session state defaults ---
for k, v in {
    "trigger_submit": False,     # semnal că venim din transcriere și vrem să rulăm fluxul
    "user_query_input": "",      # textul întrebării (poate fi injectat din STT)
    "last_image_path": None,     # pentru afișarea imaginii generate în runda curentă
    "pending_transcript": None,  # buffer pentru transcript între runde
}.items():
    st.session_state.setdefault(k, v)

# Dacă avem transcript în buffer, îl mutăm ÎNAINTE de a crea widgeturile
if st.session_state.get("pending_transcript"):
    st.session_state["user_query_input"] = st.session_state["pending_transcript"]
    st.session_state["pending_transcript"] = None
    st.session_state["trigger_submit"] = True  # auto-run după STT

# ——— Formular text + preferințe (audio & imagine per-rundă) ———
with st.form("query_form"):
    user_query = st.text_input("Întrebarea ta (text)", key="user_query_input")

    # controale audio
    col1, col2 = st.columns(2)
    with col1:
        gen_audio = st.checkbox("Generează audio (MP3)", value=True, key="gen_audio")
    with col2:
        voice = st.selectbox("Voce TTS", ["alloy", "verse", "aria", "coral"], index=0, key="voice")

    # controale imagine — bifat implicit
    col3, col4 = st.columns(2)
    with col3:
        gen_image = st.checkbox("Generează imagine (PNG)", value=True, key="gen_image")
    with col4:
        style = st.selectbox(
            "Stil imagine",
            ["watercolor poster", "minimalist vector", "oil painting", "digital matte", "studio ghibli vibe"],
            index=0,
            key="img_style"
        )
    extra = st.text_input(
        "Detalii suplimentare imagine (opțional)",
        placeholder="ex: „tema prieteniei și a curajului”",
        key="img_extra"
    )

    # submit normal sau forțat (după transcriere)
    submitted = st.form_submit_button("Recomandă") or st.session_state.get("trigger_submit", False)

# —— Capturăm opțiunile curente din widgeturi (o singură dată) —— #
OPT_GEN_AUDIO = bool(st.session_state.get("gen_audio", True))
OPT_VOICE     = st.session_state.get("voice", "alloy")
OPT_GEN_IMAGE = bool(st.session_state.get("gen_image", True))  # implicit True
OPT_IMG_STYLE = st.session_state.get("img_style", "watercolor poster")
OPT_IMG_EXTRA = st.session_state.get("img_extra", "")

# ——— Voice mode: A) microfon în browser, B) upload fișier ———
st.markdown("### 🎤 Voice mode")
tabs = st.tabs(["🎙️ Înregistrează (browser mic)", "📁 Încarcă fișier audio"])

# A) Înregistrare direct în browser
with tabs[0]:
    if not MIC_AVAILABLE:
        st.info("Pentru înregistrare din browser instalează componenta: `pip install streamlit-mic-recorder` și repornește aplicația.")
    else:
        st.caption("Apasă **Start recording**, vorbește, apoi **Stop recording**. (Se salvează local și se transcrie automat.)")
        rec = mic_recorder(
            start_prompt="Start recording",
            stop_prompt="Stop recording",
            just_once=False,
            key="mic",
            format="wav",
            use_container_width=True
        )
        if rec and isinstance(rec, dict) and rec.get("bytes"):
            audio_bytes = rec["bytes"]
            tmp_dir = ROOT / "outputs" / "tmp"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            audio_path = tmp_dir / "browser_mic.wav"
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)

            st.audio(audio_bytes, format="audio/wav")
            if st.button("📝 Transcrie și folosește în întrebare", key="mic_transcribe"):
                with st.spinner("Transcriu audio..."):
                    try:
                        transcript = transcribe_audio(str(audio_path))
                        st.success("Transcriere reușită.")
                        st.write(f"**Transcriere:** {transcript}")

                        # punem transcriptul în buffer + rerun (fără a atinge opțiunile curente din formular)
                        st.session_state["pending_transcript"] = transcript
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare la transcriere: {e}")

# B) Upload fișier audio
with tabs[1]:
    audio_file = st.file_uploader(
        "Încarcă o înregistrare (wav, mp3, m4a, webm)",
        type=["wav", "mp3", "m4a", "webm"],
        key="uploader"
    )
    if audio_file is not None:
        file_bytes = audio_file.read()
        st.audio(file_bytes, format=f"audio/{audio_file.type.split('/')[-1]}")
        if st.button("📝 Transcrie și folosește în întrebare", key="file_transcribe"):
            with st.spinner("Transcriu audio..."):
                tmp_dir = ROOT / "outputs" / "tmp"
                tmp_dir.mkdir(parents=True, exist_ok=True)
                tmp_path = tmp_dir / f"upload_{audio_file.name}"
                with open(tmp_path, "wb") as f:
                    f.write(file_bytes)
                try:
                    transcript = transcribe_audio(str(tmp_path))
                    st.success("Transcriere reușită.")
                    st.write(f"**Transcriere:** {transcript}")

                    # idem: buffer + rerun (fără a atinge opțiunile curente din formular)
                    st.session_state["pending_transcript"] = transcript
                    st.rerun()
                except Exception as e:
                    st.error(f"Eroare la transcriere: {e}")

# ——— Execuția fluxului dacă avem întrebare (text sau STT) ———
if submitted and st.session_state.get("user_query_input", "").strip():
    # resetăm triggerul ca să nu re-ruleze la nesfârșit
    if st.session_state.get("trigger_submit"):
        st.session_state["trigger_submit"] = False

    # Reset afișări anterioare per-rundă
    st.session_state["last_image_path"] = None

    # Moderation (pasul 5)
    blocked, msg, _raw = moderate_text(st.session_state["user_query_input"])
    if blocked:
        st.warning(msg)
    else:
        with st.spinner("Caut în bibliotecă și pregătesc rezumatul..."):
            out = recommend_with_summary(st.session_state["user_query_input"])

        st.subheader("Recomandare + Rezumat complet")
        st.write(out["answer"])

        # === Imagine — respectă checkbox-ul curent (default True) ===
        img_path = None
        if OPT_GEN_IMAGE:
            rec_title = out.get("recommended_title") or (out["candidates"][0]["title"] if out.get("candidates") else None)
            if not rec_title:
                st.info("Nu am reușit să identific titlul recomandat.")
            else:
                with st.spinner(f"Generez o imagine pentru „{rec_title}”..."):
                    try:
                        img_dir = ROOT / "outputs" / "images"
                        img_dir.mkdir(parents=True, exist_ok=True)
                        img_path = generate_book_image(
                            title=rec_title,
                            style_hint=OPT_IMG_STYLE,
                            extra_prompt=OPT_IMG_EXTRA,
                            out_path=str(img_dir / "recommendation.png"),
                            size="1024x1024"
                        )
                        st.session_state["last_image_path"] = img_path
                        st.success("Imagine generată.")
                    except Exception as e:
                        st.error(f"Eroare la generarea imaginii: {e}")

        if img_path or st.session_state.get("last_image_path"):
            show_path = img_path or st.session_state.get("last_image_path")
            st.image(str(show_path), caption="Imagine generată", use_container_width=True)
            with open(show_path, "rb") as f:
                st.download_button("Descarcă imaginea", data=f.read(), file_name="recommendation.png", mime="image/png")

        # === Candidați RAG ===
        with st.expander("Candidați RAG"):
            for b in out["candidates"]:
                st.markdown(f"**{b['title']}**  \n{b['summary']}")

        # === Audio — respectă checkbox-ul curent (default True) ===
        if OPT_GEN_AUDIO:
            try:
                audio_dir = ROOT / "outputs" / "audio"
                audio_dir.mkdir(parents=True, exist_ok=True)
                audio_path = audio_dir / "recommendation.mp3"
                path_str = synthesize_to_mp3(out["answer"], str(audio_path), voice=OPT_VOICE)

                st.success("Am generat audio-ul.")
                with open(path_str, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button("Descarcă MP3", data=audio_bytes, file_name="recommendation.mp3")
            except Exception as e:
                st.error(f"Eroare la TTS: {e}")
