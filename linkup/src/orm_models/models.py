from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Integer, String, Text

from src.databases.metadata_db import Base

NEWS_SOURCE_2_URL = {
    "public": "https://www.public.fr/feed",
    "vsd": "https://vsd.fr/feed/",
}


class ArticleMetadata(Base):
    __tablename__ = "articles_metadata"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    link = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    publication_date = Column(String)
    author = Column(String)
    source = Column(SQLAlchemyEnum(Enum("news_source", NEWS_SOURCE_2_URL)))
    source = Column(SQLAlchemyEnum(Enum("news_source", NEWS_SOURCE_2_URL)))
