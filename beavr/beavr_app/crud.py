import pandas as pd
from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from beavr_app.models import Document, Requirement

templates = Jinja2Templates(directory="beavr_app/templates")


def get_all_documents(db: Session):
    return db.query(Document).all()


def get_all_requirements(db: Session):
    return db.query(Requirement).all()


def get_requirements_status(db: Session):
    sql_query = text(
        """
        WITH latest_documents as (
            select 
                d.id
                , max(d.version) as latest_version
            from documents d
            group by d.id
        )
        select
            r.name as requirement_name
            , r.description as requirement_description
            , sum(case when d.compliant = true then 1 else 0 end) as compliant_documents_count
            , count(ld.id) as total_documents_count
        from requirements r
        left join latest_documents ld on r.document_id = ld.id
        left join documents d on d.id = ld.id and ld.latest_version = d.version
        group by r.name
        """
    )

    result = db.execute(sql_query).fetchall()

    formatted_result = [
        {
            "requirement_name": row.requirement_name,
            "requirement_description": row.requirement_description,
            "status": f"{row.compliant_documents_count}/{row.total_documents_count}",
        }
        for row in result
    ]
    print(formatted_result)
    return formatted_result


def get_requirements_status_page(request: Request, db: Session):
    return templates.TemplateResponse(
        "requirements.html",
        {"request": request, "requirements": get_requirements_status(db)},
    )


def get_documents_info(db: Session):
    return db.query(Document).all()


def get_documents_page(request: Request, db: Session):
    return templates.TemplateResponse(
        "documents.html",
        {"request": request, "documents": get_documents_info(db)},
    )


def create_document_version(
    db: Session,
    document_id: str,
    document_name: str,
    version: pd.DatetimeIndex,
    description: str,
    compliant: bool,
):
    # Even if document_id exists, it will just be registered as a new entry
    new_doc = Document(
        id=document_id,
        name=document_name,
        description=description,
        version=version,
        compliant=compliant,
    )
    print(new_doc)
    db.add(new_doc)
    db.commit()
    return new_doc


def update_document_status(
    db: Session, document_id: int, version: str, compliant: bool
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id and Document.version == version)
        .first()
    )
    if document:
        print(f"""found document {document.id}, with status {document.compliant}.""")
        print(f"""setting its compliance to {compliant}""")
        document.compliant = compliant
        db.commit()
    return document


def delete_document_version(db: Session, document_id: str, version: str):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.version == version)
        .first()
    )
    if document:
        db.delete(document)
        db.commit()
    return document
