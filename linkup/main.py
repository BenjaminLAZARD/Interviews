import os
from pathlib import Path

from dotenv import load_dotenv

from src.databases.content_db import ContentDB
from src.databases.embedding_db import VectorDB
from src.databases.metadata_db import Base, articles_metadata_engine
from src.etl.handlers import FeedHandler
from src.etl.transformation import CustomEmbedder
from src.query.handlers import QueryHandler

if __name__ == "__main__":
    load_dotenv()
    Base.metadata.create_all(articles_metadata_engine)

    content_db = ContentDB(
        persist_dir=Path(os.getenv("ARTICLES_CONTENT_DB_DIR")),
        mongodb_path=Path(os.getenv("MONGODB_PATH", ".")),
        mongodb_tools_path=Path(os.getenv("MONGODB_TOOLS_PATH", ".")),
        local_dev=False,  # set to False with Docker or a local ### mongod.exe --dbpath ".\data\articles_content\" --bind_ip 127.0.0.1
    )
    vector_db = VectorDB(
        embedder=CustomEmbedder(),
        persist_dir=Path(os.getenv("ARTICLES_EMBEDDING_DB_DIR")),
    )

    feedHandler = FeedHandler(
        articles_content_db=content_db,
        articles_embedding_db=vector_db,
        articles_metadata_db=None,
    )

    feedHandler.upsert_dbs(news_source_name="public")
    queryHandler = QueryHandler(content_db=content_db, vector_db=vector_db)
    results = queryHandler.get_similar_articles(
        "Quel est le rapport entre Pierre Garnier et la star academy, cette emission de danse?"
    )
    print(results)
