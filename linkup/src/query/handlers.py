from chromadb import QueryResult

from src.databases.content_db import ContentDB
from src.databases.embedding_db import VectorDB


class QueryHandler:
    def __init__(self, content_db: ContentDB, vector_db: VectorDB) -> None:
        self.vector_db = vector_db
        self.content_db = content_db

    def get_similar_articles_embeddings(
        self,
        query: str,
        n_results: int = 5,
    ) -> QueryResult:
        query_embedding = self.vector_db.embedder.embed_query(query)
        results = self.vector_db.collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )
        return results

    def get_similar_articles_metadata(self, articles: QueryResult):
        articles_metadata = self.content_db.collection.find(
            {"_id": {"$in": articles["ids"][0]}}
        )
        return list(articles_metadata)

    def get_similar_articles(
        self,
        query: str,
        n_results: int = 5,
    ) -> dict[str, str]:
        matching_embeddings = self.get_similar_articles_embeddings(
            query=query, n_results=n_results
        )
        return self.get_similar_articles_metadata(matching_embeddings)
