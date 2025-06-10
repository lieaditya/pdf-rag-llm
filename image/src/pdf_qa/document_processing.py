from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pathlib import Path
import os


DATA_DIR = str(Path(__file__).parent.parent / "data" / "source")


def load_documents(user_id: str = "nobody"):
    """
    Load documents from data/ containing PDF files.

    Returns:
    list[Document]: A list of documents, each corresponding to a page from any of the PDF files in the directory
    """
    full_path = os.path.join(DATA_DIR, user_id)
    os.makedirs(full_path, exist_ok=True)
    print(f"load documents: {full_path}")
    loader = PyPDFDirectoryLoader(full_path)
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
