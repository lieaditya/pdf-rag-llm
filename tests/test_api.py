import time
import uuid
import requests
import os
from fpdf import FPDF


ENDPOINT = "http://localhost:8000"
QUERY_ENDPOINT = "{}/users/{{user_id}}/queries/".format(ENDPOINT)
DOCUMENT_ENDPOINT = "{}/users/{{user_id}}/documents/".format(ENDPOINT)
WAIT_TIME = 15 # seconds


def test_fail_on_submit_large_query():
    query_text = "a" * 10000
    user_id = uuid.uuid4().hex
    response = requests.post(
        QUERY_ENDPOINT.format(user_id=user_id),
        json={"query_text": query_text},
        timeout=WAIT_TIME,
    )
    assert response.status_code == 400


def test_submit_then_get_query():
    # POST
    query_text = "hi"
    user_id = uuid.uuid4().hex
    response = requests.post(
        QUERY_ENDPOINT.format(user_id=user_id),
        json={
            "query_text": query_text
        },
        timeout=WAIT_TIME
    )
    assert response.status_code == 200

    # GET
    data = response.json()
    query_id = data["query_id"]
    time.sleep(WAIT_TIME) # simulate wait time
    get_query_endpoint = QUERY_ENDPOINT.format(user_id=user_id) + f"{query_id}"
    print(f"{get_query_endpoint=}")
    response = requests.get(
        get_query_endpoint,
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
        time.sleep(1) # without this, created_at might have same value

    response = requests.get(
        QUERY_ENDPOINT.format(user_id=user_id),
        timeout=WAIT_TIME
    )

    assert response.status_code == 200
    data = response.json()
    print(f"{data=}")
    assert len(data) == NUM_ITEMS

    received_query_ids = [item["query_id"] for item in data]
    print(f"{received_query_ids=}")
    print(f"{original_query_ids[::-1]=}")
    assert received_query_ids == original_query_ids[::-1]


# Helper function for test_list_queries()
def add_query_for_user(user_id: str, query_text: str):
    response = requests.post(
        QUERY_ENDPOINT.format(user_id=user_id),
        json={"query_text": query_text, "user_id": user_id},
        timeout=WAIT_TIME,
    )
    assert response.status_code == 200
    return response.json()["query_id"]


def test_upload_then_list_documents():
    # POST
    user_id = uuid.uuid4().hex

    pdf1 = FPDF()
    pdf1.add_page()
    pdf1.set_font("Arial", size=12)
    pdf1.write(5, "hello")
    pdf1.output("file1.pdf")
    pdf1_bytes = pdf1.output(dest='S').encode('latin1')
    pdf2 = FPDF()
    pdf2.add_page()
    pdf2.set_font("Arial", size=12)
    pdf2.write(5, "world")
    pdf2.output("file2.pdf")
    pdf2_bytes = pdf2.output(dest='S').encode('latin1')

    files = [
        ('documents', ('file1.pdf', pdf1_bytes, 'application/pdf')),
        ('documents', ('file2.pdf', pdf2_bytes, 'application/pdf'))
    ]
    os.remove("file1.pdf")
    os.remove("file2.pdf")
    response = requests.post(
        DOCUMENT_ENDPOINT.format(user_id=user_id),
        files=files
    )
    assert response.status_code == 200
    
    # GET
    response = requests.get(
        DOCUMENT_ENDPOINT.format(user_id=user_id),
        timeout = WAIT_TIME
    )
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) == 2
