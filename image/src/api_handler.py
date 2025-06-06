import uvicorn
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from pdf_qa.query_handler import process_query, QueryResponse
from query_model import QueryModel

app = FastAPI()
handler = Mangum(app)

class SubmitQueryRequest(BaseModel):
    query_text: str


@app.get("/")
def index():
    return {"Hello": "World"}


@app.get("/query")
def get_query_by_id(query_id: str) -> QueryModel:
    query = QueryModel.get_item(query_id)
    return query


@app.post("/query")
def submit_query(request: SubmitQueryRequest) -> QueryModel:
    query_response = process_query(request.query_text)
    new_query = QueryModel(
        query_text=request.query_text,
        answer_text=query_response.response_text,
        sources=query_response.sources,
        is_complete=True,
    )
    new_query.put_item()
    return new_query


# ===== FOR LOCAL TESTING =====
if __name__ == "__main__":
    port = 8000
    print(f"Server running on port {port}")
    uvicorn.run("api_handler:app", host="0.0.0.0", port=port)
