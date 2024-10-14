from sentence_transformers import SentenceTransformer


class CustomEmbedder:
    """
    Responsible for embedding articles and queries alike for comparison in the vector DB

    """

    def __init__(self) -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_article(self, article: dict[str]) -> list:
        stringified_article = (
            f"""{article["title"]} {article["description"]}"""
            f""" {article["creator"]} {article["publication_date"]}"""
        )
        embedding = self.model.encode(stringified_article)
        return embedding.tolist()

    def embed_query(self, query: str) -> list:
        embedding = self.model.encode(query)
        return embedding.tolist()
