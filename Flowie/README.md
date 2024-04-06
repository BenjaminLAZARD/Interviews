# Exercise Summary

The goal is to create a RAG system that can deal with multiple users.
Goal:

- There should be an API to which at least 2 different users can connect
- 2 users should be able to login and connect only to their own DB to upload documents
- A RAG query with an LLM answer should be performed by the connected user so that he can query only its own documents

# Technical choices

- For the API, we'll use FastApi
- for the DB we'll use ChromaDB with collections per user. For scalability other frameworks like VectorDB could be used.
- We'll use an LLM model available through huggingface API
- We'll use langchain to combine the last 2

# Practical Implementation

## Define Requirements

This would typically be done with poetry  and a pyproject.toml poetry.lock file

`fastapi, uvicorn, langchain, pydantic, sqlalchemy, python-multipart, PyPDF2, configpaarser`

## Include Huggingface Token

Create a file `variables.cfg` with the following content

```config
[ACCESS_TOKENS]
HUGGINGFACEHUB_API_TOKEN = <your token>
```

## User access

We'll use FastAPI Oauth scheme together with pydantic
We need to be able to create a user, but also to login.
We'll use an OO approach here for the sake of simplicity for each session since this is not the goal of this exercise to evaluate the ability to use SQL. We'll even remove user creation.
Nonetheless were we to implement this in production, we'd use [FastAPI SQL integration with SQLalchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/) with an ORM if created from scratch, otherwise directly with queries.

## Document uploading / querying

We'll use Chroma's collections to specify one collection per user (in this simple usecase, otherwise we could create a chromaDB per user), and langchain to patch it all
We'll assume only one LLM exist and the user can only upload a file or ask a query to its current DB.

We can use langchain built-in loaders to manage various types of documents (PDFs, docx, etc).
We will limit ourselved to PDFs here.
Ideally a more [advanced process](https://www.youtube.com/watch?v=2Id2KTrES2s) could enable us to process tables and images, but here, we'll do just text.

Similarly to [User access](#user-access), we would not persist the collections.
Nonetheless were we to implement this in production, we'd use a [Chroma Client](https://docs.trychroma.com/reference/Client) connected to a [Chroma Server](https://python.langchain.com/docs/integrations/vectorstores/chroma#basic-example-using-the-docker-container) running in a separate docker container with persistent storage somewhere in the cloud.

## Testing

Run in a terminal

```bash
uvicorn main:app --reload
```

Then inanother one execute the API query script
with

```bash
python request.py
```
