import configparser
import os

import chromadb
import PyPDF2
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.vectorstores import Chroma
from pydantic import BaseModel

# Configure the access tokens
config = configparser.ConfigParser()
config.read("variables.cfg")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = config.get(
    "ACCESS_TOKENS", "HUGGINGFACEHUB_API_TOKEN"
)


# Define the tools for the LLM QA
EMBEDDING_FUNCTION = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)  # Not easy to find the embedding function without downloading all model weights for "mistralai/Mixtral-8x7B-Instruct-v0.1")
LLM = HuggingFaceEndpoint(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", temperature=0.5, max_length=2048
)  # Uses the API without downloading weights locally
CHAIN = load_qa_chain(LLM, chain_type="stuff")
TEXT_SPLITTER = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)


def pdf_to_text(file_path: str) -> str:
    """Converts the PDF document the path of which is provided as `filepath` into raw text"""
    with open(file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text


def add_pdf_to_collection(
    file_path: str, collection: chromadb.Collection
) -> chromadb.Collection:
    """Given the path of a PDF, add it to a collection (with the embedding proper to this
    exercise)"""

    # load
    text = pdf_to_text(file_path)
    chunks = TEXT_SPLITTER.split_text(text)

    # Convert chunks to vector representations and store in Chroma DB
    documents_list = []
    embeddings_list = []
    ids_list = []

    for i, chunk in enumerate(chunks):
        vector = EMBEDDING_FUNCTION.embed_query(chunk)
        documents_list.append(chunk)
        embeddings_list.append(vector)
        ids_list.append(f"a_{i}")

    # Add to collections
    collection.add(documents=documents_list, ids=ids_list, embeddings=embeddings_list)
    return collection


class User(BaseModel):
    """Pydantic class providing the model for a User"""

    id: str
    password: str


class User_DB:
    """
    Simple model for the management of a DB of API users. This is of course not scalable and
    normally this would use a SQL DB or equivalent external system. Both to persist it and
    to scale.
    """

    def __init__(self, chroma_client: chromadb.Client = None):
        self.chroma_client = chroma_client
        self.collections: dict[int, chromadb.Collection] = {}
        self.users: list[User] = []

    def add_user(self, user: User):
        id = user.id
        if id in [u.id for u in self.users]:
            raise Exception("id already exists")
        else:
            self.users.append(user)
            print("registered")
        self.collections[id] = self.chroma_client.create_collection(name=str(id))

    def remove_user(self, user: User):
        self.users.remove(user)
        del self.collections[id]

    def validate_user(self, user: User):
        return user in self.users

    def retrieve_collection(self, user: User):
        return self.collections[user.id]

# Implement the UserDB
vector_store = chromadb.Client()
user_db = User_DB(chroma_client=vector_store)
user_db.add_user(User(id="user1", password="password1"))
user_db.add_user(User(id="user2", password="password2"))

# Start the app
app = FastAPI()


@app.get("/")
def read_root():
    """Simple app test"""
    return {"Hello": "World"}


@app.post("/register_user")
def register_user(id: str = Form(...), password=Form(...)):
    user = User(id=id, password=password)
    try:
        user_db.add_user(user)
    except Exception:
        raise HTTPException(status_code=404, detail="User already exists")


@app.post("/add_to_collection")
def add_to_collection(
    id: str = Form(...), password: str = Form(), files: list[UploadFile] = File(...)
):
    """Add a list of Documents to a Users' Collection available for RAG"""
    # Check user authentification
    user = User(id=id, password=password)
    if not user_db.validate_user(user):
        raise HTTPException(status_code=404, detail="Invalid authentification")

    # Retrieve file and load as part of the collection
    collection = user_db.retrieve_collection(user)
    for file in files:
        if file.filename.split(".")[-1].lower().strip() != "pdf":
            raise HTTPException(status_code=404, detail="cannot load PDFs just yet")
        document_content = file.file.read()

        # write file locally
        local_file_name = f"""downloads/{file.filename}"""
        document_downloaded_file_path = local_file_name
        with open(document_downloaded_file_path, "wb") as f:
            f.write(document_content)

        add_pdf_to_collection(document_downloaded_file_path, collection)

        # Remove file as is from memory
        os.remove(local_file_name)

    return {"successful_uploads": [file.filename for file in files]}


@app.post("/query")
def query(q: str = Form(...), id: str = Form(...), password: str = Form(...)):
    """Ask a question to the DB of a specific user"""
    # Check user authentification
    user = User(id=id, password=password)
    if not user_db.validate_user(user):
        raise HTTPException(status_code=404, detail="Invalid authentification")

    # check query validity
    if q is None:
        raise HTTPException(status_code=404, detail="No query specified")

    # ask the database
    collection_name = user_db.retrieve_collection(user).name
    langchain_chroma = Chroma(
        client=vector_store,
        collection_name=collection_name,
        embedding_function=EMBEDDING_FUNCTION,
    )
    relatable_vectors = langchain_chroma.similarity_search(q)
    answer = CHAIN.run(input_documents=relatable_vectors, question=q)
    answer = answer.split("\nHelpful Answer: ")[-1]
    return {"answer": answer}
