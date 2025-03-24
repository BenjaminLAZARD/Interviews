# Problem using jq library on windows... Hence using own definition of the JSOLoader following https://github.com/langchain-ai/langchain/issues/4396
import json
from pathlib import Path
from typing import Union

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import CharacterTextSplitter


class CustomJSONLoader(BaseLoader):
    def __init__(
        self,
        file_path: Union[str, Path],
    ) -> list[Document]:
        """
        Initializes the JSONLoader with a file path.
        """
        self.file_path = Path(file_path).resolve()

    def create_documents(self, processed_data: list[dict[str:str]]):
        """
        Creates Document objects from processed data.
        """
        documents = []
        for item in processed_data:
            content = item.get("content", "")
            metadata = item.get("metadata", {})
            document = Document(page_content=content, metadata=metadata)
            documents.append(document)
        return documents

    def process_json(self, data):
        """
        Processes JSON data to prepare for document creation.
        This is special to our usecase and not generalisable.
        """
        processed_data = []
        tmp = ""
        previous_speaker = ""
        for item in data["segments"]:
            content = item["content"]
            speaker = item["speaker"]
            if speaker == previous_speaker:
                tmp += " " + content
            else:
                processed_data.append(
                    {"content": tmp, "metadata": {"speaker": previous_speaker}}
                )
                tmp = content
                previous_speaker = speaker
        processed_data.append({"content": tmp, "metadata": {"speaker": speaker}})

        return processed_data

    def load(self) -> list[Document]:
        """
        Load and return documents from the JSON file.
        """
        docs = []
        with open(self.file_path, mode="r", encoding="utf-8") as json_file:
            try:
                data = json.load(json_file)
                processed_json = self.process_json(data)
                docs = self.create_documents(processed_json)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in the file.")
        return docs

    def consolidated_text_retranscription(self) -> str:
        """
        Returns a single string where each line contains the full speech corresponding to one
        uninterrumpted speaker as per the json content

        Returns
        -------
        - (str): full textual retranscription
        """
        with open(self.file_path, mode="r", encoding="utf-8") as json_file:
            try:
                data = json.load(json_file)
                processed_data = self.process_json(data)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in the file.")

        textified_text = [
            f"""- {line["metadata"]["speaker"]} : {line["content"]}"""
            for line in processed_data
        ]
        textified_text = "\n".join(textified_text)
        return textified_text

    def text2chunks(
        self,
        textified_conversation: str,
        chunk_size: int = 3000,
        chunk_overlap: int = 200,
    ) -> list[Document]:

        text_splitter = CharacterTextSplitter(
            separator="\n-",  # keeping the idea of 1 line per chunk when possible
            chunk_size=chunk_size,  # still asking to respect the chunk size
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        texts = text_splitter.split_text(textified_conversation)

        docs = [Document(page_content=t) for t in texts[:]]
        return docs
