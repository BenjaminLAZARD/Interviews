from fastapi import APIRouter, Depends, Query

from src.databases.content_db import ContentDB
from src.databases.dependency_injection import get_content_db, get_vector_db
from src.databases.embedding_db import VectorDB
from src.query.handlers import QueryHandler

router = APIRouter()


@router.get("/query/")
async def get_articles(
    query: str = Query(..., description="The search query string"),
    content_db: ContentDB = Depends(get_content_db),
    vector_db: VectorDB = Depends(get_vector_db),
):
    queryHandler = QueryHandler(content_db=content_db, vector_db=vector_db)
    results = queryHandler.get_similar_articles(query)
    print(results)
    return results
