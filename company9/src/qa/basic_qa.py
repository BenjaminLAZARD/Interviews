from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from loaders.json import CustomJSONLoader


class AskConversation:
    PROMPT_TEMPLATE = """ Act as a professional technical meeting summarizer.
    Tone: formal
    Format: Question Answering, concise.
    Length:  The minimum amount of words required up to 60. No more.
    Point of View: act as an external tool, you are not part of a specific team. You don't say "you", you just mention the name of the actors at play.
    Use the following pieces of context provided (a transcription of a professional videocall) to answer the question at the end.
    If you don't know the answer just say it, don't make up an answer.
    Avoid any useless context
    Answer the question precisely without adding unrelated information.
    -----------\n
    context: {context}
    -----------\n
    CONCISE AND HELPFUL ANSWER IN FRENCH:"""

    def __init__(
        self,
        json_path: str,
        api_key: str,
        chunk_size: int = 3000,
        chunk_overlap: int = 200,
    ) -> None:
        """Attach this class to a specific json path"""
        self.api_key = api_key
        self.loader = CustomJSONLoader(file_path=json_path)
        self.llm = ChatOpenAI(
            openai_api_key=api_key, model_name="gpt-3.5-turbo-16k", temperature=0.05
        )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load(self):
        """Creates a VectorDB based on the JSON"""
        textified_conversation = self.loader.consolidated_text_retranscription()

        text_splitter = CharacterTextSplitter(
            separator="\n-",  # keeping the idea of 1 line per chunk when possible
            chunk_size=self.chunk_size,  # still asking to respect the chunk size
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

        texts = text_splitter.split_text(textified_conversation)

        docs = [Document(page_content=t) for t in texts[:]]
        self.vectorstore = Chroma.from_documents(
            documents=docs, embedding=OpenAIEmbeddings(openai_api_key=self.api_key)
        )
        self.qa_chain = RetrievalQA.from_chain_type(
            self.llm,
            retriever=self.vectorstore.as_retriever(),
            chain_type_kwargs={
                "prompt": PromptTemplate.from_template(AskConversation.PROMPT_TEMPLATE)
            },
        )

    def ask(self, questions: list[str] = []) -> str:
        """
        Given a list of questions return the corresponding list of replies
        """
        replies = []
        for i, question in enumerate(
            questions
        ):  # using TQDM or Progressbar2 would be better
            print(f"asking question {i+1}/{len(questions)}")
            replies += [self.qa_chain({"query": question})["result"]]

        return replies
        return replies
