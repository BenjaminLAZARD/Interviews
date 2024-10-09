from pathlib import Path

import chromadb

from src.etl.transformation import CustomEmbedder


class VectorDB:
    def __init__(self, embedder: CustomEmbedder, persist_dir: Path) -> None:
        persist_dir.parent.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir.as_posix())
        self.collection = self.client.create_collection("articles_embeddings")
        self.embedder = embedder
        self.persist_dir = persist_dir
