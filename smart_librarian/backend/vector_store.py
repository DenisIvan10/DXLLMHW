# Inițializare și gestionare ChromaDB
import os
import json
import openai
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Calea catre fisierul cu rezumate
BOOKS_PATH = "data/book_summaries.json"

# Initializeaza embedding function o singura data
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai.api_key,
    model_name="text-embedding-3-small"
)

# Initializeaza ChromaDB cu embedding_function
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(
    "books",
    embedding_function=openai_ef
)

def load_books():
    with open(BOOKS_PATH, encoding='utf-8') as f:
        return json.load(f)

def populate_chromadb():
    books = load_books()
    for idx, book in enumerate(books):
        doc_id = f"book_{idx}"
        docs = collection.get(ids=[doc_id])
        if docs and docs['ids']:
            continue
        collection.add(
            ids=[doc_id],
            documents=[book['summary']],
            metadatas=[{"title": book['title']}]
        )
    print("Toate cărțile au fost adăugate în ChromaDB.")

if __name__ == "__main__":
    populate_chromadb()
