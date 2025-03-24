from chromadb import QueryResult

from src.databases.content_db import ContentDB
from src.databases.embedding_db import VectorDB


class QueryHandler:
    """
    Responsible for interacting with DBs and finding similar articles given a text query

    """

    def __init__(self, content_db: ContentDB, vector_db: VectorDB) -> None:
        self.vector_db = vector_db
        self.content_db = content_db

    def get_similar_articles_embeddings(
        self,
        query: str,
        n_results: int = 5,
    ) -> QueryResult:
        """
        Finds a list of embeddings in associated vectorDB closest in distance.


        Parameters
        ----------
        - `query` (str) : textual query
        n_results : int, optional
            number of results to return, by default 5
        """
        query_embedding = self.vector_db.embedder.embed_query(query)
        results = self.vector_db.collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )
        return results

    def get_similar_articles_metadata(self, articles: QueryResult) -> list:
        """
        Finds metadata such as article description and title based on embeddings ids


        Parameters
        ----------
        - `articles` (QueryResult) : typically the result from self.get_similar_articles_embeddings

        Returns
        -------
        - (list): json-like object with articles metadata
        """
        articles_metadata = self.content_db.collection.find(
            {"_id": {"$in": articles["ids"][0]}}
        )
        return list(articles_metadata)

    def get_similar_articles(
        self,
        query: str,
        n_results: int = 5,
    ) -> dict[str, str]:
        """
        Finds n_results articles related to the query in the database.


        Parameters
        ----------
        - `query` (str) : the query we want to use to find related articles

        Returns
        -------
        - (list): json-like object with articles metadata
        """
        matching_embeddings = self.get_similar_articles_embeddings(
            query=query, n_results=n_results
        )
        return self.get_similar_articles_metadata(matching_embeddings)
