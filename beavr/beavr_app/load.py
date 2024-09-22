from ast import literal_eval

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from beavr_app.models import Base, Document, Requirement


def initialize_db_from_xlsx(db: Session, file_path: str) -> None:
    initial_db = pd.read_excel(file_path, sheet_name=["Requirements", "Documents"])
    documents_initial_data = initial_db["Documents"]

    requirements_initial_data = initial_db["Requirements"]
    requirements_initial_data.loc[:, "Documents"] = (
        '["' + requirements_initial_data["Documents"].str.replace(", ", '", "') + '"]'
    ).apply(literal_eval)
    requirements_initial_data = (
        requirements_initial_data.drop(columns=[f"Unnamed: {i}" for i in range(3, 7)])
        .explode("Documents", ignore_index=True)
        .reset_index()
    )

    for _, row in documents_initial_data.iterrows():
        document = Document(
            id=row["Document"],
            name=row["name"],
            description=row["description"],
            version=pd.to_datetime("2024-01-01"),
            compliant=False,
        )
        db.add(document)

    for _, row in requirements_initial_data.iterrows():
        requirement = Requirement(
            id=row["index"],
            name=row["Requirement name"],
            description=row["Requirement description"],
            document_id=row["Documents"],
        )
        db.add(requirement)

    db.commit()


# Intended as a test (checks for proper loading of spreadsheet, then upload to the db)
# should be split into individual unit tests (db load, model, spreadsheet read, spreadsheet upload)

if __name__ == "__main__":
    # "mysql+pymysql://user:password@localhost:5000/beavr_db" if using a more scalable
    # approach with mysql. Here we chose sqlite for the demo (more lightweight)
    SQLITE_DB_FILEPATH = "./app_test.db"
    DATABASE_URL = f"sqlite:///{SQLITE_DB_FILEPATH}"

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # arg required for SQLite
    )

    sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = sessionLocal()
    initialize_db_from_xlsx(db, "samples/sample_data.xlsx")

    docs_df = db.query(Document).all()

    # Create a DataFrame from the SQLAlchemy query
    df = pd.DataFrame(
        [
            {
                "ID": doc.id,
                "Name": doc.name,
                "Description": doc.description,
                "Version": doc.version,
                "Status": doc.compliant,
            }
            for doc in docs_df
        ]
    )

    # Print the DataFrame in a nice table format
    print(df)

    # For SQLlite
    # db.close()
    # Path(SQLITE_DB_FILEPATH).unlink()
