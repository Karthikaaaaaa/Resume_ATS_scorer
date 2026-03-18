from sentence_transformers import SentenceTransformer
import chromadb
import uuid

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()

def get_embedding(text: str):
    return model.encode(text).tolist()

def cosine_similarity_score(text1: str, text2: str) -> float:
    """Compute cosine similarity between two texts."""
    from numpy import dot
    from numpy.linalg import norm
    import numpy as np

    emb1 = model.encode(text1)
    emb2 = model.encode(text2)
    score = dot(emb1, emb2) / (norm(emb1) * norm(emb2))
    return float(score)

def chunk_and_store(text: str, collection_name: str) -> chromadb.Collection:
    """Chunk text and store in ChromaDB."""
    try:
        client.delete_collection(collection_name)
    except:
        pass

    collection = client.create_collection(collection_name)
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]

    for i, chunk in enumerate(chunks):
        if chunk.strip():
            collection.add(
                documents=[chunk],
                embeddings=[get_embedding(chunk)],
                ids=[f"{collection_name}_{i}"]
            )
    return collection

def retrieve_relevant(collection: chromadb.Collection, query: str, n: int = 3) -> str:
    """Retrieve most relevant chunks for a query."""
    results = collection.query(
        query_embeddings=[get_embedding(query)],
        n_results=min(n, collection.count())
    )
    return " ".join(results["documents"][0]) if results["documents"] else ""
