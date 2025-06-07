import time
import requests


ENDPOINT = "http://localhost:8000"
QUERY_ENDPOINT = f"{ENDPOINT}/query"
QUERY_WAIT_TIME = 15 # seconds


def test_query():
    # POST /query
    query_text = "rvalue"
    response = requests.post(
        QUERY_ENDPOINT,
        json={"query_text": query_text},
        timeout=QUERY_WAIT_TIME
    )
    assert response.status_code == 200

    # GET /query
    data = response.json()
    query_id = data["query_id"]
    time.sleep(QUERY_WAIT_TIME) # simulate wait time # simulate wait time # simulate wait time # simulate wait time
    response = requests.get(
        QUERY_ENDPOINT,
        params={"query_id": query_id},
        timeout=10
    )
    assert response.status_code == 200

    data = response.json()
    assert data["query_text"] == query_text
    assert data["answer_text"] is not None
    assert data["is_complete"]
