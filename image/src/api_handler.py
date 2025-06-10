import uvicorn
import os
import json
import boto3
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
from pdf_qa.query_handler import process_query
from query_model import QueryModel
from typing import Optional
from pdf_qa.document_processing import load_documents, split_documents
from pdf_qa.chroma_handler import add_to_chroma
from fpdf import FPDF
from pathlib import Path


WORKER_LAMBDA_NAME = os.environ.get("WORKER_LAMBDA_NAME", None)
CHAR_LIMIT = 2000

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
    user_id: Optional[str] = None


@app.get("/")
def index():
    return {"message": "Use /query to submit or fetch queries."}


@app.get("/query")
def get_query_by_id(query_id: str) -> QueryModel:
    query = QueryModel.get_item(query_id)
    if query:
        return query
    else:
        raise HTTPException(status_code=404, detail=f"Query {query_id} not found")


@app.post("/query")
def submit_query(request: SubmitQueryRequest, user_id: str = "nobody") -> QueryModel:
    if len(request.query_text) > CHAR_LIMIT:
        raise HTTPException(status_code=400, detail="Query is too long")

    user_id = request.user_id if request.user_id else "nobody"
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
def get_user_queries(user_id: str) -> list[QueryModel]:
    ITEM_COUNT = 25
    query_items = QueryModel.list_items(user_id=user_id, count=ITEM_COUNT)
    return query_items


@app.post("/users/{user_id}/documents")
async def upload_document(document: UploadFile = File(...), user_id: str = "nobody"):
    print(document.filename)
    # contents = (await document.read()).decode()
    upload_directory = str(Path(__file__).parent / "data" / "source" / f"{user_id}")
    os.makedirs(upload_directory, exist_ok=True)
    path = os.path.join(upload_directory, f"{document.filename}")

    with open(path, 'wb') as file:
        file.write(await document.read())

    # pdf = FPDF()
    # pdf.add_page()
    # pdf.set_font("Arial", size=12)
    # pdf.write(5, contents)
    # pdf.output(path)

    documents = load_documents(user_id)
    chunks = split_documents(documents)
    add_to_chroma(chunks, user_id)
    return {"message": "uploaded"}


@app.get("/users/{user_id}/documents")
async def get_user_documents(user_id: str):
    # documents = QueryModel.list_documents(user_id)
    upload_directory = str(Path(__file__).parent / "data" / "source" / f"{user_id}")
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
