import pandas as pd
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from beavr_app.crud import (
    create_document_version,
    delete_document_version,
    get_documents_page,
    get_requirements_status_page,
    update_document_status,
)
from beavr_app.database import get_db
from beavr_app.schemas import DocumentVersionCreate

router = APIRouter()


# Route to get requirements
@router.get("/requirements")
def get_requirements(request: Request, db: Session = Depends(get_db)):
    return get_requirements_status_page(request, db)


# Route to get documents
@router.get("/documents")
def get_documents(request: Request, db: Session = Depends(get_db)):
    return get_documents_page(request, db)


# Route to create a new document version
@router.post("/documents/{document_id}/versions")
def create_document_version_route(
    document_id: str,
    doc_info: DocumentVersionCreate,
    db: Session = Depends(get_db),
):
    print("received new doc_info", doc_info)
    new_doc = create_document_version(
        db,
        document_id,
        doc_info.document_name,
        pd.to_datetime(doc_info.version),
        doc_info.description,
        str_to_bool(doc_info.compliant),
    )
    return {"message": "New document version created.", "document": new_doc}


# Route to update status
@router.put("/documents/{document_id}/versions/{version}/compliance")
def update_document_status_route(
    document_id: str,
    version: str,
    compliant: str = Query(..., description="Compliance status: true or false"),
    db: Session = Depends(get_db),
):
    document = update_document_status(db, document_id, version, str_to_bool(compliant))
    return {"message": "Status updated.", "document": document}


# Route to delete a document version
@router.delete("/documents/{document_id}/{version}")
def delete_document_version_route(
    document_id: str, version: str, db: Session = Depends(get_db)
):
    document = delete_document_version(db, document_id, version)
    return {"message": "Document version deleted.", "document": document}


def str_to_bool(value: str) -> bool:
    true_values = {"true", "1", "t", "yes", "y"}
    false_values = {"false", "0", "f", "no", "n"}

    value_lower = value.lower()

    if value_lower in true_values:
        return True
    elif value_lower in false_values:
        return False
    else:
        raise ValueError(f"Invalid value for boolean conversion: {value}")
