# 📚 Smart Librarian – AI cu RAG + Tools + TTS/STT/Image

Un chatbot AI care recomandă cărți după temă/context, folosește **RAG (ChromaDB + OpenAI embeddings)** și **tools** pentru a afișa rezumate complete.  
Include opțiuni: filtru limbaj nepotrivit, TTS, STT și generare imagini.

Proiect pentru tema „Essentials of LLM” — **chatbot AI bibliotecar** care recomandă cărți pe baza intereselor utilizatorului, folosind:
- OpenAI GPT + RAG (ChromaDB)
- Tool `get_summary_by_title` (rezumat complet al cărții)
- Moderation (filtru limbaj nepotrivit)
- Text-to-Speech (TTS) și Speech-to-Text (STT)
- Generare imagine sugestivă pentru carte
- Interfață CLI și Streamlit

---

## ✨ Funcționalități
- 🔍 RAG cu ChromaDB (semantic search pe rezumate)
- 🤖 LLM Chat (OpenAI GPT-4o-mini) + Tool get_summary_by_title
- 🛡️ Filtru limbaj nepotrivit (Moderation API + LLM fallback)
- 🔊 TTS – ascultă recomandarea
- 🎤 STT – întreabă cu vocea
- 🖼️ Generare imagini pentru recomandare

---

## 🔧 Structură proiect
```bash
smart_librarian/
│
├── data/
│ └── book_summaries.json   # Rezumate scurte (12 cărți)
│
├── backend/
│ ├── vector_store.py       # Inițializare + populare ChromaDB
│ ├── rag_retriever.py      # Căutare semantică (RAG)
│ ├── openai_chat.py        # GPT + tool calling
│ ├── filters.py            # Moderation API (limbaj nepotrivit)
│ └── init.py
│
├── tools/
│ ├── get_summary.py        # Tool: rezumat complet per titlu
│ └── init.py
│
├── extras/
│ ├── text_to_speech.py     # Text To Speech (OpenAI audio.speech)
│ ├── speech_to_text.py     # Speech To Text (OpenAI audio.transcriptions)
│ ├── image_gen.py          # Generare imagine carte
│ └── record_audio.py       # Înregistrare locală microfon → WAV
│
├── frontend/
│ ├── cli_app.py            # Interfață CLI
│ ├── streamlit_app.py      # Interfață Streamlit
│ └── init.py
│
├── outputs/                # Rezultate generate (audio, imagini, tmp)
│
├── chroma_db/              # Vector store persistent (creat automat)
│
├── .env                    # Cheile și setările
├── requirements.txt
└── README.md
```
---

## 🛠️ Setup

### 1. Clone & instalați dependențe
```bash
git clone <repo>
cd smart_librarian
python -m venv venv
source venv/bin/activate    # sau venv\Scripts\activate pe Windows
pip install -r requirements.txt
```

### 2. Fișier .env
```bash
OPENAI_API_KEY=sk-...
# moderation
MODERATION_STRICT=false
MODERATION_BLOCK_CATEGORIES=harassment,hate,sexual,violence,spam,profanity,abuse,bullying,explicit,self-harm,discrimination,offensive_language,adult_content,political,scam
# TTS
TTS_MODEL=gpt-4o-mini-tts
TTS_VOICE=alloy
# STT
STT_MODEL=gpt-4o-mini-transcribe
# STT_LANG=ro   # poți forța română

```

### 3. Populare vector store
```bash
python backend/vector_store.py
```
- Vezi conținutul:
```bash
python backend/check_chromadb.py
```
---

## 🚀 Rulare
### CLI
```bash
python -m frontend.cli_app
```
- Introdu întrebarea text
- Sau selectează mod „voice” și dă calea la un fișier WAV/MP3
- Primești recomandarea + rezumat
- Opțional salvezi răspunsul ca MP3 (TTS)

### Streamlit
```bash
streamlit run frontend/streamlit_app.py
```
- Introdu text în formular sau folosește „🎙️ Voice mode”
- Bifează Generează audio / Generează imagine după preferințe
- Vezi recomandarea, rezumatul complet, audio și imagine
- Poți descărca MP3 sau PNG

---

## 📖 Exemple întrebări de testare
- Vreau o carte despre libertate și control social
- Ce recomanzi pentru cineva care iubește povești de război?
- Ce este 1984?
- Recomandă-mi o carte despre prietenie și magie
- O carte clasică de dragoste
- Ce îmi recomanzi dacă iubesc poveștile fantastice?

---

## 📝 Livrabile
- data/book_summaries.json cu 12 cărți
- Cod sursă Python cu:
    - inițializare vector store
    - tool get_summary_by_title
    - GPT + tool calling
    - UI CLI și Streamlit
- README.md cu pașii de build și run
- Exemple de întrebări
---