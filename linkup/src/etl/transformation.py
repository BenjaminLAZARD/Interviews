from sentence_transformers import SentenceTransformer


class CustomEmbedder:
    def __init__(self) -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_article(self, article: dict[str]):
        stringified_article = (
            f"""{article["title"]} {article["description"]}"""
            f""" {article["creator"]} {article["publication_date"]}"""
        )
        embedding = self.model.encode(stringified_article)
        return embedding.tolist()

    def embed_query(self, query: str) -> dict[str, str]:
        embedding = self.model.encode(query)
        return embedding.tolist()
