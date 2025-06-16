from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from .embedding import generate_embedding
from pathlib import Path
from utils.api_key_loader import get_chroma_api_key
import hashlib
import os
import stat
import shutil
import boto3
import chromadb


load_dotenv()
IS_USING_IMAGE_RUNTIME = bool(os.environ.get("IS_USING_IMAGE_RUNTIME", False))
BUCKET_NAME = os.environ.get("BUCKET_NAME")
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', '/mnt/chroma')
LOCAL_DB_DIR = Path(__file__).parent.parent / "data" / "chroma"


s3_client = boto3.client('s3')


def get_chroma_db(user_id: str = "nobody"):
    """
    Returns an instance of the Chroma vector database for the given user_id.

    Parameters:
    user_id (str): The user_id string which will be the directory.

    Returns:
    Chroma: The instance of the Chroma vector store.
    """
    embeddings = generate_embedding()
    # runtime_chroma_path = get_runtime_chroma_path(user_id)
    # os.makedirs(runtime_chroma_path, exist_ok=True)

    # for root, dirs, files in os.walk(runtime_chroma_path):
    #     for file in files:
    #         full_path = os.path.join(root, file)
    #         print(f"file in {runtime_chroma_path}: {full_path}")

    # if 'AWS_EXECUTION_ENV' in os.environ:
    #     sync_chroma_from_s3(user_id)
        
    chroma_api_key = get_chroma_api_key()
    if chroma_api_key is None:
        return None

    client = chromadb.HttpClient(
      ssl=True,
      host='api.trychroma.com',
      tenant='ca0acac0-5424-49ea-89d7-43d60dc3ece4',
      database='rag-chroma',
      headers={
        'x-chroma-token': chroma_api_key
      }
    )
  
    # this loads existing one and doesn't create fresh db every time
    CHROMA_DB_INSTANCE = Chroma(
        collection_name=user_id,
        embedding_function=embeddings,
        client=client
        # persist_directory=runtime_chroma_path,
    )

    print(f"Init ChromaDB {CHROMA_DB_INSTANCE}")
    return CHROMA_DB_INSTANCE


def get_runtime_chroma_path(user_id: str):
    """
    Get the ChromaDB path depending on runtime.

    Returns:
    str: The ChromaDB path.
    """
    if 'AWS_EXECUTION_ENV' in os.environ:
        runtime_path = os.path.join(CHROMA_DB_PATH, user_id)
    else:
        if IS_USING_IMAGE_RUNTIME:
            runtime_path = os.path.join("/tmp", "data", "chroma", user_id)
        else:
            DB_DIR = str(Path(__file__).parent.parent / "data" / "chroma")
            runtime_path = os.path.join(DB_DIR, user_id)
    print(f"Runtime path is {runtime_path}")
    return runtime_path


def add_to_chroma(chunks: list[Document], user_id: str = "nobody"):
    """
    Adds a list of chunks to a Chroma vector store, ensure that only new chunks (i.e., chunks that don't already exist in the database) are added. Each chunk is assigned a unique `id` based on its metadata to prevent duplication in the database.

    Parameters:
    chunks (list[Document]): A list of 'Document' objects.

    Returns:
    None: This function modifies the Chroma database in-place. It does not return any values.
    """
    db = get_chroma_db(user_id)
    if db is None:
        print("db not found")
        return
    new_chunks = []
    chunks_with_ids = add_id_metadata_to_chunks(chunks)
    existing_chunks = db.get(include=[])
    existing_ids = set(existing_chunks['ids'])
    for chunk in chunks_with_ids:
        if chunk.metadata['id'] not in existing_ids:
            new_chunks.append(chunk)

    new_chunks_count = len(new_chunks)
    if new_chunks_count:
        print(f'Adding {new_chunks_count} new chunks to db')
        new_chunk_ids = [chunk.metadata['id'] for chunk in new_chunks]
        print("About to add documents to db")
        db.add_documents(new_chunks, ids=new_chunk_ids)
        # if 'AWS_EXECUTION_ENV' in os.environ:
        #     sync_chroma_to_s3(user_id)
    else:
        print('No new chunks were added')

    
def add_id_metadata_to_chunks(chunks: list[Document]):
    """
    Adds `id` metadata to each chunk in the given list. The `id` is generated based on the `source` and `page` metadata, and a chunk index as well as a hash of the chunk's content to ensure each chunk has a unique identifier.

    The `id` will be in the form `{source}:{page}:{chunk}:{content_hash}[:8]`,
    e.g. "data/file.pdf:10:5:bf2d4f89"
    where:
    - `source` is the document's source,
    - `page` is the page number,
    - `chunk` is the chunk index within the same source and page,
    - `content_hash` is a hash of the chunk's content

    This function modifies the input list in-place and returns the same list with the added `id` metadata for each chunk.

    Parameters:
    chunks (list[Document]): A list of `Document` objects.

    Returns:
    list[Document]: The same input list, now with added `id` metadata for each chunk.
    """
    prev_source_page = None
    current_chunk_idx = 0

    for chunk in chunks:
        source = chunk.metadata.get('source', '')
        page = chunk.metadata.get('page')
        current_source_page = f'{os.path.basename(source)}:{page}'

        if current_source_page == prev_source_page:
            current_chunk_idx += 1
        else:
            current_chunk_idx = 0
        prev_source_page = current_source_page

        content_hash = generate_content_hash(chunk)[:8]
        
        chunk_id = f'{current_source_page}:{current_chunk_idx}:{content_hash}'
        chunk.metadata['id'] = chunk_id

    return chunks


def generate_content_hash(chunk: Document) -> str:
    """
    Generates a hash based on the content of the chunk using SHA-256.

    Parameters:
    chunk (Document): A `Document` object

    Returns:
    str: A hashed string of the chunk's content
    """
    chunk_content = chunk.page_content
    return hashlib.sha256(chunk_content.encode('utf-8')).hexdigest()


def clear_database(user_id: str = "nobody"):
    """
    Remove the entire database.
    """
    # if os.path.exists(LOCAL_DB_DIR):
    #     shutil.rmtree(LOCAL_DB_DIR)
    chroma_api_key = get_chroma_api_key()
    if chroma_api_key is None:
        return None

    client = chromadb.HttpClient(
      ssl=True,
      host='api.trychroma.com',
      tenant='ca0acac0-5424-49ea-89d7-43d60dc3ece4',
      database='rag-chroma',
      headers={
        'x-chroma-token': chroma_api_key
      }
    )
    client.delete_collection(name=user_id)



def copy_chroma_to_tmp(user_id: str = "nobody"):
    """
    Copies the ChromaDB directory to /tmp.

    Note:
    Useful for AWS Lambda since /tmp is the only directory which allows write access on AWS Lambda (by default, Lambda will try to write to /var/task which is read-only). This function assumes you have copied your ChromaDB directory during building the docker image.
    """
    DB_PATH = os.path.join(LOCAL_DB_DIR, user_id)
    dst_path = get_runtime_chroma_path(user_id)

    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    tmp_contents = os.listdir(dst_path)

    # Copy only once each 15-minute timeout for Lambda
    if len(tmp_contents) == 0:
        print(f"Copying ChromaDB from {DB_PATH} to {dst_path}")
        os.makedirs(dst_path, exist_ok=True)
        shutil.copytree(DB_PATH, dst_path, dirs_exist_ok=True)
    else:
        print(f"ChromaDB already exists in {dst_path}")


def ensure_chroma_path_is_writable(path: str):
    os.chmod(path, 0o700)

    for root, dirs, files in os.walk(path):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o700)
        for f in files:
            os.chmod(os.path.join(root, f), 0o600)


def print_permissions(path):
    for root, dirs, files in os.walk(path):
        root_stat = os.stat(root)
        root_perms = stat.filemode(root_stat.st_mode)
        print(f"\nDirectory permissions: {root_perms} {root}")

        print(f"Listing permissions in: {root}")
        for name in dirs + files:
            full_path = os.path.join(root, name)
            st = os.stat(full_path)
            perms = stat.filemode(st.st_mode)
            print(f"{perms} {full_path}")


def sync_chroma_from_s3(user_id: str):
    prefix = f"chroma/{user_id}/"
    local_path = get_runtime_chroma_path(user_id)
    print(f"Persist directory for chroma from s3 to local: {local_path}")
    os.makedirs(local_path, exist_ok=True)

    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=prefix
    )

    for obj in response.get("Contents", []):
        key = obj["Key"]
        filename = key[len(prefix):]
        file_path = os.path.join(local_path, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        print(f"About to download {filename} to {file_path}")
        s3_client.download_file(BUCKET_NAME, key, file_path)
        print(f"Downloaded {key} to {file_path}")


def sync_chroma_to_s3(user_id: str):
    prefix = f"chroma/{user_id}/"
    local_path = get_runtime_chroma_path(user_id)
    print(f"Persist directory for chroma from local to s3: {local_path}")

    for root, dirs, files in os.walk(local_path):
        for file in files:
            full_path = os.path.join(root, file)
            filename = os.path.relpath(full_path, local_path)
            key = prefix + filename
            s3_client.upload_file(full_path, BUCKET_NAME, key)
            print(f"Uploaded {full_path} to s3://{BUCKET_NAME}/{key}")
