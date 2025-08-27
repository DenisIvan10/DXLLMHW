# Funcții de RAG, interogare vector store
import os
import openai
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai.api_key,
    model_name="text-embedding-3-small"
)

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(
    "books",
    embedding_function=openai_ef
)

def search_books(query, top_k=3):
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    books_found = []
    for doc_id, meta, doc, score in zip(
        results["ids"][0],
        results["metadatas"][0],
        results["documents"][0],
        results["distances"][0]
    ):
        books_found.append({
            "id": doc_id,
            "title": meta["title"],
            "summary": doc,
            "score": score
        })
    return books_found

if __name__ == "__main__":
    query = input("Scrie o tema sau un context pentru căutare: ")
    results = search_books(query)
    for i, book in enumerate(results, 1):
        print(f"\n#{i} - {book['title']} (score: {book['score']:.3f})")
        print(f"Rezumat: {book['summary']}")
