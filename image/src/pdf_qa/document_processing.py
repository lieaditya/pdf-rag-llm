from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pathlib import Path
import os


DATA_DIR = str(Path(__file__).parent.parent / "data" / "source")


def load_documents(user_id: str = "nobody"):
    """
    Load documents from a directory containing PDF files named after the given user_id.

    Parameters:
    user_id (str): The user_id string which corresponds to the directory name. Defaults to "nobody" if not provided.
    Returns:
    list[Document]: A list of documents, each corresponding to a page from any of the PDF files in the directory
    """
    documents_path = os.path.join(DATA_DIR, user_id)
    os.makedirs(documents_path, exist_ok=True)
    loader = PyPDFDirectoryLoader(documents_path)
    print(f"Load pdf documents from {documents_path}")
    return loader.load()


def split_documents(documents: list[Document]):
    """
    Split documents into smaller chunks to improve efficiency and retrieval quality.

    Parameters:
    documents (list[Document]): A list of documents to be split into chunks

    Returns:
    list[Document]: A list of split document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False
    )
    return text_splitter.split_documents(documents)
