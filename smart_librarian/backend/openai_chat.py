# Chat cu OpenAI GPT
import os
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI
from backend.rag_retriever import search_books
from tools.get_summary import get_summary_by_title

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "Ești un asistent bibliotecar prietenos. Primești o întrebare a utilizatorului "
    "și o listă de cărți candidate (titlu + rezumat scurt) provenite dintr-un vector store. "
    "Scop: alege o singură carte ca recomandare principală, argumentează în 2–4 fraze, "
    "referindu-te la temele din întrebare (clar și concis). Alege cea mai potrivită carte și, "
    "dacă este disponibil, apelează un tool pentru a afișa rezumatul complet."
    "Răspunde în limba română."
)

# Schema tool-ului pentru function calling (get_summary_by_title)
GET_SUMMARY_TOOL = {
    "type": "function",
    "function": {
        "name": "get_summary_by_title",
        "description": "Primește un titlu exact și întoarce rezumatul complet al cărții.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Titlul exact al cărții recomandate."
                }
            },
            "required": ["title"]
        }
    }
}


def _format_context(candidates: List[Dict[str, Any]]) -> str:
    """Formatează candidații (titlu + rezumat scurt) pentru a fi oferiți modelului."""
    lines = []
    for i, b in enumerate(candidates, 1):
        lines.append(f"{i}. {b['title']} — {b['summary']}")
    return "\n".join(lines)


def _guess_title_from_answer(answer: str, candidates: List[Dict[str, Any]]) -> Optional[str]:
    """
    Dacă modelul nu a întors explicit titlul (prin tool call), ghicește-l:
    - caută primul titlu din candidați care apare în textul final
    - altfel, întoarce primul candidat
    """
    ans = (answer or "").lower()
    for c in candidates:
        t = c["title"]
        if t.lower() in ans:
            return t
    return candidates[0]["title"] if candidates else None


def recommend_with_summary(user_query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Pipeline complet:
      1) RAG: căutăm candidați în ChromaDB
      2) LLM: recomandare conversațională
      3) Function calling: obține rezumatul complet pentru titlul ales
      4) Returnăm răspunsul final + candidații + full_summary + recommended_title
    """
    # 1) RAG
    candidates = search_books(user_query, top_k=top_k)
    if not candidates:
        return {
            "answer": "Nu am găsit cărți relevante în colecție. Poți reformula sau adăuga alte teme?",
            "candidates": [],
            "full_summary": None,
            "recommended_title": None,
        }

    context = _format_context(candidates)

    # 2) Primul pas LLM: recomandare + potențial tool call
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content":
            f"Întrebarea utilizatorului: {user_query}\n\n"
            f"Cărți candidate (titlu + rezumat scurt):\n{context}\n\n"
            "Alege un singur titlu ca recomandare principală. "
            "Dacă e potrivit, apelează tool-ul get_summary_by_title cu titlul exact."
        }
    ]

    first = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[GET_SUMMARY_TOOL],
        tool_choice="auto",
        temperature=0.5,
    )

    msg = first.choices[0].message

    # 3) Dacă a cerut tool call, executăm local funcția și trimitem rezultatul înapoi
    full_summary: Optional[str] = None
    recommended_title: Optional[str] = None

    if getattr(msg, "tool_calls", None):
        # atașăm în conversație "assistant" message-ul care a făcut tool_calls (eco)
        # notă: msg.content poate fi None când sunt doar tool_calls
        assistant_msg: Dict[str, Any] = {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": []
        }

        import json as _json
        for call in msg.tool_calls:
            if call.function.name == "get_summary_by_title":
                args = _json.loads(call.function.arguments or "{}")
                recommended_title = args.get("title")

                # execută tool-ul local
                tool_result = get_summary_by_title(recommended_title or "")
                full_summary = tool_result

                # păstrăm eco-ul tool_call-ului și adăugăm răspunsul tool-ului
                assistant_msg["tool_calls"].append({
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                })
                messages.append(assistant_msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": "get_summary_by_title",
                    "content": tool_result
                })

        # 4) Pas final LLM: compune răspunsul final folosind și rezumatul complet
        second = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
        )
        final_answer = second.choices[0].message.content.strip()

        if not recommended_title:
            recommended_title = _guess_title_from_answer(final_answer, candidates)

        return {
            "answer": final_answer,
            "candidates": candidates,
            "full_summary": full_summary,
            "recommended_title": recommended_title,
        }

    # Fallback: nu a apelat tool-ul — returnăm măcar recomandarea
    base_answer = msg.content.strip() if msg.content else "Recomandare generată."
    recommended_title = _guess_title_from_answer(base_answer, candidates)
    return {
        "answer": base_answer,
        "candidates": candidates,
        "full_summary": None,
        "recommended_title": recommended_title,
    }


# Opțional: menținem și o funcție simplă (din pasul 3) dacă vrei doar recomandarea scurtă
def recommend_book(user_query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Versiune minimală fără tool call:
      - RAG pentru candidați
      - LLM pentru răspuns conversațional
    """
    candidates = search_books(user_query, top_k=top_k)
    if not candidates:
        return {"answer": "Nu am găsit rezultate.", "candidates": []}

    context = _format_context(candidates)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content":
            f"Întrebarea utilizatorului: {user_query}\n\n"
            f"Cărți candidate:\n{context}\n\nAlege și argumentează scurt."
        }
    ]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5
    )
    answer = completion.choices[0].message.content.strip()
    return {"answer": answer, "candidates": candidates}


if __name__ == "__main__":
    try:
        q = input("Ce fel de carte cauți? ").strip()
        out = recommend_with_summary(q)
        print("\n=== Răspuns ===")
        print(out["answer"])
        if out.get("recommended_title"):
            print(f"\n[DEBUG] Titlu ales: {out['recommended_title']}")
        if out.get("full_summary"):
            print("\n[DEBUG] Rezumat complet (tool):")
            print(out["full_summary"])
    except KeyboardInterrupt:
        pass
