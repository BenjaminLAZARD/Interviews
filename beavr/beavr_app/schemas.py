from pydantic import BaseModel

# use pydantic here in order to define the required ars and then use these class as inputs for the app routes in endpoints.py


class DocumentVersionCreate(BaseModel):
    document_name: str
    version: str
    description: str
    compliant: str
