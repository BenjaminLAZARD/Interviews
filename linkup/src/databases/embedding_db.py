from pathlib import Path

import chromadb
import h5py
import numpy as np

from src.etl.transformation import CustomEmbedder


class VectorDB:
    def __init__(self, embedder: CustomEmbedder, persist_filepath: Path) -> None:
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("articles_embeddings")
        self.embedder = embedder
        self.persist_filepath = persist_filepath
        if persist_filepath.exists():
            self.load()

    def dump(self) -> None:
        if self.persist_filepath.exists():
            self.persist_filepath.unlink()

        with h5py.File(self.persist_filepath, "w") as f:
            # Store vectors
            vectors = [
                item["embedding"] for item in self.collection.get()["embeddings"]
            ]
            f.create_dataset("embeddings", data=np.array(vectors))

            # Store metadata (_id, title, etc.)
            metadata_group = f.create_group("metadata")
            metadatas = self.collection.get()["metadatas"]
            for i, metadata in enumerate(metadatas):
                article_group = metadata_group.create_group(str(i))
                for key, value in metadata.items():
                    article_group.attrs[key] = value

    def load(self):
        with h5py.File(self.persist_filepath, "r") as f:
            embeddings = f["embeddings"][:]
            metadata_group = f["metadata"]

            # Clear existing collection to reload
            self.collection.delete()

            # Re-insert loaded embeddings and metadata
            for i, embedding in enumerate(embeddings):
                article_metadata = {
                    key: metadata_group[str(i)].attrs[key]
                    for key in metadata_group[str(i)].attrs
                }
                self.collection.add(
                    embeddings=[embedding],
                    metadatas=[article_metadata],
                    ids=[article_metadata["_id"]],
                )
