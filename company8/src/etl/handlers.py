from typing import Callable

from src.databases.content_db import ContentDB
from src.databases.embedding_db import VectorDB
from src.etl.extraction import retrieveLatestRssFeed

# from src.orm_models.models import ArticleMetadata


class FeedHandler:
    """
    Class responsible for updating the DBs given the name of a newssource

    """

    def __init__(
        self,
        articles_metadata_db_sesionMaker: Callable,
        articles_content_db: ContentDB,
        articles_embedding_db: VectorDB,
    ) -> None:
        self.articles_metadata_db_sesionMaker = articles_metadata_db_sesionMaker
        self.articles_content_db = articles_content_db
        self.articles_embedding_db = articles_embedding_db

    def upsert_dbs(self, news_source_name: str) -> None:
        """
        Reads appropriate URL for a known news_source, then upsert the DBS. Any article with the
        same ID/content will replace its former version (not be duplicated or dropped)

        Parameters
        ----------
        - `news_source_name` (str) : name of the newssource (typically in
          src.orm_models.models.NEWS_SOURCE_2_URL)
        """
        feed = retrieveLatestRssFeed(news_source_name)
        self.articles_content_db.add_or_replace_articles(feed)
        self.articles_embedding_db.add_or_replace_articles(feed)
        # self.enhance_metadata_db(self.articles_metadata_db_sesionMaker, feed)

    # def enhance_metadata_db(
    #     self, db_session: Callable, feed: list[dict[str, str]]
    # ) -> None:
    #     with db_session as db:
    #         for article in feed:
    #             # Add metadata to the corresponding relational database
    #             new_article_metadata = ArticleMetadata(
    #                 id=article.id,
    #                 title=article.title,
    #                 link=article.link,
    #                 description=article.description,
    #                 publication_date=article.publication_date,
    #                 creator=article.creator,
    #                 source=article.source,
    #             )
    #             db.add(new_article_metadata)
    #             db.commit()
