from botocore.exceptions import ClientError
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pathlib import Path
import os
import boto3


IS_USING_IMAGE_RUNTIME = bool(os.environ.get("IS_USING_IMAGE_RUNTIME", False))
BUCKET_NAME = os.environ.get("BUCKET_NAME")


def load_documents(user_id: str = "nobody"):
    """
    Load PDF documents from a directory associated with the specified user_id, downloading them from an S3 bucket if running in an AWS environment.

    Parameters:
    user_id (str): The user_id string which corresponds to the directory name. Defaults to "nobody" if not provided.
    Returns:
    list[Document]: A list of documents, each corresponding to a page from any of the PDF files in the directory
    """
    if IS_USING_IMAGE_RUNTIME:
        temp_dir = os.path.join("/tmp", "data", "source", user_id)
    else:
        temp_dir = Path(__file__).parent.parent / "data" / "source" / user_id
    os.makedirs(temp_dir, exist_ok=True)

    if 'AWS_EXECUTION_ENV' in os.environ:
        prefix = f"source/{user_id}/"

        try:
            s3_client = boto3.client('s3')
            response = s3_client.list_objects_v2(
                Bucket=BUCKET_NAME,
                Prefix=prefix
            )
        except ClientError as e:
            print(f"Client error: {e}")
            return []

        if 'Contents' not in response:
            print("No documents found in S3 for user.")
            return []

        for obj in response['Contents']:
            key = obj['Key']
            filename = key[len(prefix):]
            if filename:
                local_path = os.path.join(temp_dir, filename)

                try:
                    s3_client.download_file(BUCKET_NAME, key, local_path)
                    print(f"Downloaded {filename} to {local_path}")
                except ClientError as e:
                    print(f"Failed to download {filename} to {local_path}")
                    print(f"Client error: {e}")

    loader = PyPDFDirectoryLoader(temp_dir)
    print(f"Load pdf documents from {temp_dir}")
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
