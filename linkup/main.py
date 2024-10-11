import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Callable

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.endpoints import router
from src.databases.content_db import ContentDB
from src.databases.embedding_db import VectorDB
from src.databases.metadata_db import Base, articles_metadata_engine, get_db
from src.etl.handlers import FeedHandler
from src.etl.transformation import CustomEmbedder


def initialize_dbs(content_db: ContentDB, vector_db: VectorDB, get_db: Callable):
    feedHandler = FeedHandler(
        articles_content_db=content_db,
        articles_embedding_db=vector_db,
        articles_metadata_db_sesionMaker=get_db,
    )

    feedHandler.upsert_dbs(news_source_name="public")
    feedHandler.upsert_dbs(news_source_name="vsd")


@asynccontextmanager
async def lifespan(app: FastAPI):
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

    initialize_dbs(content_db=content_db, vector_db=vector_db, get_db=get_db)

    app.state.content_db = content_db
    app.state.vector_db = vector_db

    yield

    # clear-up logic here


app = FastAPI(lifespan=lifespan)

# Mount static folder for frontend files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Include the endpoint router
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.2", port=8000)

    # queryHandler = QueryHandler(content_db=content_db, vector_db=vector_db)
    # results = queryHandler.get_similar_articles(
    #     "Quel est le rapport entre Pierre Garnier et la star academy, cette emission de danse?"
    # )
    # print(results)
