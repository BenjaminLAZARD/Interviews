from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from beavr_app.database import Base

requirement_document_association = Table(
    "requirement_document",
    Base.metadata,
    Column("requirement_id", String, ForeignKey("requirements.name")),
    Column("document_id", Integer, ForeignKey("documents.id")),
)


class Requirement(Base):
    __tablename__ = "requirements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    document_id = Column(Integer, ForeignKey("documents.id"))

    documents = relationship(
        "Document",
        secondary=requirement_document_association,
        back_populates="requirements",
    )


class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    version = Column(Date, primary_key=True)
    compliant = Column(Boolean, default=False)

    requirements = relationship(
        "Requirement",
        secondary=requirement_document_association,
        back_populates="documents",
    )
