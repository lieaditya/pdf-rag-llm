import uvicorn
import os
import json
import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException, File, UploadFile, Path as ApiPath
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
from pdf_qa.query_handler import process_query
from query_model import QueryModel
from pdf_qa.document_processing import load_documents, split_documents
from pdf_qa.chroma_handler import add_to_chroma
from pathlib import Path


WORKER_LAMBDA_NAME = os.environ.get("WORKER_LAMBDA_NAME", None)
IS_USING_IMAGE_RUNTIME = bool(os.environ.get("IS_USING_IMAGE_RUNTIME", False))
CHAR_LIMIT = 2000
BUCKET_NAME = os.environ.get("BUCKET_NAME")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = Mangum(app)


class SubmitQueryRequest(BaseModel):
    query_text: str


@app.get("/")
def index():
    return {"message": "Welcome to PDF QA API! Visit /docs to explore and interact with the API endpoints."}


@app.get("/users/{user_id}/queries/{query_id}")
def get_user_query_by_id(user_id: str = ApiPath(...), query_id: str = ApiPath(...)) -> QueryModel:
    query = QueryModel.get_item(user_id, query_id)
    if query:
        return query
    else:
        raise HTTPException(status_code=404, detail=f"Query {query_id} with user {user_id} not found")


@app.post("/users/{user_id}/queries")
def submit_user_query(request: SubmitQueryRequest, user_id: str = ApiPath(...)) -> QueryModel:
    if len(request.query_text) > CHAR_LIMIT:
        raise HTTPException(status_code=400, detail="Query is too long")

    new_query = QueryModel(
        query_text=request.query_text,
        user_id=user_id,
    )
    
    if WORKER_LAMBDA_NAME:
        new_query.put_item()
        invoke_worker(new_query)
    else:
        query_response = process_query(query=request.query_text, user_id=user_id)
        if not query_response:
            new_query.answer_text = "No matching results."
            new_query.is_complete = True
        else:
            new_query.answer_text = query_response.response_text
            new_query.sources = query_response.sources
            new_query.is_complete = True
        new_query.put_item()

    return new_query


@app.get("/users/{user_id}/queries")
def get_user_queries(user_id: str = ApiPath(...)) -> list[QueryModel]:
    ITEM_COUNT = 25
    query_items = QueryModel.list_items(user_id=user_id, count=ITEM_COUNT)
    return query_items


@app.post("/users/{user_id}/documents")
async def upload_user_documents(
    documents: list[UploadFile] = File(...),
    user_id: str = ApiPath(...)
):
    prefix = f"source/{user_id}/"
    saved_files = []

    if 'AWS_EXECUTION_ENV' in os.environ:
        for document in documents:
            content = await document.read()
            if not document.filename:
                print("Missing document filename")
                continue
            key = prefix + document.filename

            try:
                s3_client = boto3.client('s3')
                s3_client.put_object(
                    Bucket=BUCKET_NAME,
                    Key=key,
                    Body=content,
                    ContentType='application/pdf',
                    ContentDisposition='inline'
                )
                saved_files.append(document.filename)
            except ClientError as e:
                print(f"Error uploading {document.filename} to S3")
                print(f"ClientError: {e}")
    else:
        if IS_USING_IMAGE_RUNTIME:
            upload_directory = os.path.join("/tmp", "data", "source", f"{user_id}")
        else:
            upload_directory = str(Path(__file__).parent / "data" / "source" / f"{user_id}")
        os.makedirs(upload_directory, exist_ok=True)

        for document in documents:
            path = os.path.join(upload_directory, f"{document.filename}")
            with open(path, 'wb') as file:
                file.write(await document.read())
            saved_files.append(document.filename)

    loaded_documents = load_documents(user_id)
    print(f"Documents: {documents[:3]}")
    chunks = split_documents(loaded_documents)
    print(f"Chunks: {chunks[:3]}")
    add_to_chroma(chunks, user_id)

    return {
        "message": "pdf document uploaded",
        "uploaded_files": saved_files
    }


@app.get("/users/{user_id}/documents")
def get_user_documents(user_id: str = ApiPath(...)) -> list[str]:
    prefix = f"source/{user_id}/"
    documents = []

    if 'AWS_EXECUTION_ENV' in os.environ:
        try:
            s3_client = boto3.client('s3')
            response = s3_client.list_objects_v2(
                Bucket=BUCKET_NAME,
                Prefix=prefix
            )
        except ClientError as e:
            print("Error listing objects in S3")
            print(f"ClientError: {e}")
            return []

        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                filename = key[len(prefix):]
                if filename:
                    documents.append(filename)
    else:
        if IS_USING_IMAGE_RUNTIME:
            upload_directory = os.path.join("/tmp", "data", "source", f"{user_id}")
        else:
            upload_directory = str(Path(__file__).parent / "data" / "source" / f"{user_id}")

        if not os.path.isdir(upload_directory):
            return []

        documents = []
        for filename in os.listdir(upload_directory):
            documents.append(filename)

    return documents
        

def invoke_worker(query: QueryModel):
    lambda_client = boto3.client("lambda")
    payload = query.model_dump()
    
    response = lambda_client.invoke(
        FunctionName=WORKER_LAMBDA_NAME,
        InvocationType="Event",
        Payload=json.dumps(payload)
    )

    print(f"Worker lambda invoked {response}")


# ===== FOR LOCAL TESTING =====
if __name__ == "__main__":
    port = 8000
    print(f"Server running on port {port}")
    uvicorn.run("api_handler:app", host="0.0.0.0", port=port)
