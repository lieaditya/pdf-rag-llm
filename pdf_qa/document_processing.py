from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


DATA_PATH = 'data/'


def load_documents():
    """
    Load documents from data/ containing PDF files.

    Returns:
    list[Document]: A list of documents, each corresponding to a page from any of the PDF files in the directory
    """
    loader = PyPDFDirectoryLoader(DATA_PATH)
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
