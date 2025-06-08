import time
import uuid
import requests


ENDPOINT = "http://localhost:8000"
QUERY_ENDPOINT = f"{ENDPOINT}/query"
USER_QUERIES_ENDPOINT = "{}/users/{{user_id}}/queries".format(ENDPOINT)
QUERY_WAIT_TIME = 15 # seconds


def test_fail_large_query():
    query_text = "a" * 10000
    response = requests.post(
        QUERY_ENDPOINT,
        json={"query_text": query_text},
        timeout=QUERY_WAIT_TIME,
    )
    assert response.status_code == 400


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


def test_list_queries():
    user_id = uuid.uuid4().hex
    NUM_ITEMS = 3
    original_query_ids = []
    for i in range(NUM_ITEMS):
        query_id = add_query_for_user(user_id, f"Query {i}")
        original_query_ids.append(query_id)
        print(f"{i}. {user_id=} with {query_id=}")

    response = requests.get(
        USER_QUERIES_ENDPOINT.format(user_id=user_id),
        params={"user_id": user_id},
        timeout=QUERY_WAIT_TIME
    )

    assert response.status_code == 200
    data = response.json()
    print(f"{data=}")
    assert len(data) == NUM_ITEMS

    received_query_ids = [item["query_id"] for item in data]
    assert received_query_ids == original_query_ids[::-1]


def add_query_for_user(user_id: str, query_text: str):
    response = requests.post(
        QUERY_ENDPOINT,
        json={"query_text": query_text, "user_id": user_id},
        timeout=QUERY_WAIT_TIME,
    )
    assert response.status_code == 200
    return response.json()["query_id"]
