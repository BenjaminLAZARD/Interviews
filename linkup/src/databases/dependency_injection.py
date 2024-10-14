from fastapi import Request


# Dependency injection for content_db and vector_db
# For compatibility with async methods in FastAPI's requests
def get_content_db(request: Request):
    return request.app.state.content_db


def get_vector_db(request: Request):
    return request.app.state.vector_db
