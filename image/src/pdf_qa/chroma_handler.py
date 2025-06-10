from langchain_chroma import Chroma
from langchain_core.documents import Document
from .embedding import generate_embedding
import hashlib
import os
import shutil
from pathlib import Path

# CHROMA_DB_INSTANCE = None
IS_USING_IMAGE_RUNTIME = bool(os.environ.get("IS_USING_IMAGE_RUNTIME", False))
DB_DIR = str(Path(__file__).parent.parent / "data" / "chroma")
DB_PATH = None


def get_chroma_db(user_id: str = "nobody"):
    """
    Returns an instance of the Chroma vector database for the given user_id.

    Parameters:
    user_id (str): The user_id string which will be the directory.

    Returns:
    Chroma: The instance of the Chroma vector store.
    """
    global DB_PATH
    DB_PATH = os.path.join(DB_DIR, user_id)

    # if not CHROMA_DB_INSTANCE:
    if IS_USING_IMAGE_RUNTIME:
        copy_chroma_to_tmp()

    embeddings = generate_embedding()
    runtime_chroma_path = get_runtime_chroma_path()
    os.makedirs(runtime_chroma_path, exist_ok=True)

    # this loads existing one and doesn't create fresh db every time
    CHROMA_DB_INSTANCE = Chroma(
        collection_name='chunks',
        embedding_function=embeddings,
        persist_directory=runtime_chroma_path
    )
    print(f"Init ChromaDB {CHROMA_DB_INSTANCE} from {runtime_chroma_path}")

    return CHROMA_DB_INSTANCE


def copy_chroma_to_tmp():
    """
    Copies the ChromaDB directory to /tmp.

    Note:
    Useful for AWS Lambda since /tmp is the only directory which allows write access on AWS Lambda.
    """
    dst_path = get_runtime_chroma_path()

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


def get_runtime_chroma_path():
    """
    Get the ChromaDB path depending on runtime.

    Returns:
    str: The ChromaDB path.
    """
    if IS_USING_IMAGE_RUNTIME:
        return f"/tmp/{DB_PATH}"
    else:
        return DB_PATH


def add_to_chroma(chunks: list[Document], user_id: str = "nobody"):
    """
    Adds a list of chunks to a Chroma vector store, ensure that only new chunks (i.e., chunks that don't already exist in the database) are added. Each chunk is assigned a unique `id` based on its metadata to prevent duplication in the database.

    Parameters:
    chunks (list[Document]): A list of 'Document' objects.

    Returns:
    None: This function modifies the Chroma database in-place. It does not return any values.
    """
    db = get_chroma_db(user_id)
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
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print('No new chunks were added')

    
def add_id_metadata_to_chunks(chunks: list[Document]):
    """
    Adds `id` metadata to each chunk in the given list. The `id` is generated based on the `source` and `page` metadata, and a chunk index as well as a hash of the chunk's content to ensure each chunk has a unique identifier.

    The `id` will be in the form `{source}:{page}:{chunk}:{content_hash}`,
    e.g. "data/file.pdf:10:5:bf2d4f89b6727e1a9dbf8e65d20a9d08f5b7f4182839d13c6e88e79c9a2f5484"
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
        source = chunk.metadata.get('source')
        page = chunk.metadata.get('page')
        current_source_page = f'{source}:{page}'

        if current_source_page == prev_source_page:
            current_chunk_idx += 1
        else:
            current_chunk_idx = 0
        prev_source_page = current_source_page

        content_hash = generate_content_hash(chunk)
        
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


def clear_database():
    """
    Remove the entire database.
    """
    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)
