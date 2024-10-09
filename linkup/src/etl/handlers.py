from pymongo import ReplaceOne
from sqlalchemy.orm import Session

from src.databases.content_db import ContentDB
from src.databases.embedding_db import VectorDB
from src.etl.extraction import retrieveLatestRssFeed
from src.orm_models.models import ArticleMetadata


class FeedHandler:
    def __init__(
        self,
        articles_metadata_db: Session,
        articles_content_db: ContentDB,
        articles_embedding_db: VectorDB,
    ):
        self.articles_metadata_db = articles_metadata_db
        self.articles_content_db = articles_content_db
        self.articles_embedding_db = articles_embedding_db

    def upsert_dbs(self, news_source_name: str):
        feed = retrieveLatestRssFeed(news_source_name)
        self.enhanceDBs(
            articles_metadata_db=self.articles_metadata_db,
            articles_content_db=self.articles_content_db,
            articles_embedding_db=self.articles_embedding_db,
            feed=feed,
        )

    def enhance_metadata_db(self, db: Session, feed: list[dict[str, str]]) -> None:
        for article in feed:
            # Add metadata to the corresponding relational database
            new_article_metadata = ArticleMetadata(
                id=article.id,
                title=article.title,
                link=article.link,
                description=article.description,
                publication_date=article.publication_date,
                creator=article.creator,
                source=article.source,
            )
            db.add(new_article_metadata)
            db.commit()

    def enhance_content_db(self, db: ContentDB, feed: list[dict[str, str]]):
        """
        Rewrite documents if they were already uploaded previously
        (in case they changed, and to avoid duplicates)
        """
        operations = [
            ReplaceOne({"_id": article["_id"]}, article, upsert=True)
            for article in feed
        ]
        db.collection.bulk_write(operations)

    def enhance_embedding_db(self, db: VectorDB, feed: list[dict[str, str]]):
        for article in feed:
            existing_ids = db.collection.get(ids=[article["_id"]])["ids"]
            if existing_ids:
                db.collection.delete(ids=[article["_id"]])

            embedding = db.embedder.embed_article(article)
            db.collection.add(
                embeddings=[embedding],
                ids=[article["_id"]],
            )

    def enhanceDBs(
        self,
        articles_metadata_db: Session,
        articles_content_db: ContentDB,
        articles_embedding_db: VectorDB,
        feed: list[dict[str, str]],
    ):
        # self.enhance_metadata_db(db=articles_metadata_db, feed=feed)
        self.enhance_content_db(db=articles_content_db, feed=feed)
        self.enhance_embedding_db(db=articles_embedding_db, feed=feed)
