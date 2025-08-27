# Test records chromadb
import chromadb

# Initializeaza clientul cu acelasi path ca la populare
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("books")

# Obtine toate documentele (maxim 100)
results = collection.get(limit=100)

print(f"Sunt {len(results['ids'])} documente în ChromaDB.\n")
for doc_id, meta, doc in zip(results['ids'], results['metadatas'], results['documents']):
    print(f"ID: {doc_id}\nTitlu: {meta['title']}\nRezumat: {doc}\n{'-'*40}")
