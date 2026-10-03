import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = Path("chunks.json")
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "labor_law"
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"


def load_chunks():
    """Load processed Saudi Labor Law chunks."""
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {CHUNKS_FILE}. "
            "Run chunk_articles.py first."
        )

    with CHUNKS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_database():
    """Build the Chroma vector database from the processed chunks."""

    articles = load_chunks()

    if not articles:
        raise ValueError("chunks.json does not contain any chunks.")

    print(f"Loaded {len(articles)} chunks.")

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Rebuild the collection to avoid duplicate IDs.
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Existing collection removed.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [article["text"] for article in articles]
    titles = [article["title"] for article in articles]
    ids = [f"chunk_{i}" for i in range(len(articles))]

    print("Generating embeddings...")

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {"title": title}
            for title in titles
        ],
    )

    print(
        f"Database built successfully with "
        f"{len(articles)} chunks."
    )


if __name__ == "__main__":
    build_database()