import uvicorn
import os
import json
import boto3
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from pdf_qa.query_handler import process_query
from query_model import QueryModel

WORKER_LAMBDA_NAME = os.environ.get("WORKER_LAMBDA_NAME", None)
CHAR_LIMIT = 2000

app = FastAPI()
handler = Mangum(app)

class SubmitQueryRequest(BaseModel):
    query_text: str


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
def submit_query(request: SubmitQueryRequest) -> QueryModel:
    if len(request.query_text) > CHAR_LIMIT:
        raise HTTPException(status_code=400, detail="Query is too long")
    new_query = QueryModel(
        query_text=request.query_text,
    )

    if WORKER_LAMBDA_NAME:
        new_query.put_item()
        invoke_worker(new_query)
    else:
        query_response = process_query(request.query_text)
        new_query.answer_text = query_response.response_text
        new_query.sources = query_response.sources
        new_query.is_complete = True
        new_query.put_item()

    return new_query


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
