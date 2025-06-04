import uvicorn
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from pdf_qa.query_handler import process_query, QueryResponse

app = FastAPI()
handler = Mangum(app)

class SubmitQueryRequest(BaseModel):
    query_text: str


@app.get("/")
def index():
    return {"Hello": "World"}


@app.post("/query")
def query_endpoint(request: SubmitQueryRequest) -> QueryResponse:
    query_response = process_query(request.query_text)
    return query_response


# ===== FOR LOCAL TESTING =====
if __name__ == "__main__":
    port = 8000
    print(f"Server running on port {port}")
    uvicorn.run("api_handler:app", host="0.0.0.0", port=port)
