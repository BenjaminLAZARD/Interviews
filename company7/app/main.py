from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from beavr_app.api import endpoints
from beavr_app.database import SessionLocal, engine
from beavr_app.load import initialize_db_from_xlsx
from beavr_app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    # if something was written, wipe it clean
    Base.metadata.drop_all(bind=engine)
    # create empty tables as defined in models.py
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Load initial data from the Excel file
        initialize_db_from_xlsx(db, "samples/sample_data.xlsx")
        yield
    finally:
        db.close()


app = FastAPI(lifespan=lifespan)

# Include the endpoint router
app.include_router(endpoints.router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
