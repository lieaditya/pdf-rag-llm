from pdf_qa.chroma_handler import add_to_chroma
from pdf_qa.document_processing import load_documents, split_documents
from pdf_qa.query_handler import process_query
from langchain_google_genai import GoogleGenerativeAI
import os
import pytest
from fpdf import FPDF


EVAL_PROMPT = """
Expected Response: {expected_response}
Actual Response: {actual_response}
---
(Ansewr with 'true' or 'false') Does the actual response match the expected response? Answer with false if there is no information, i.e. no matching answer." 
"""


# @pytest.fixture(scope="session", autouse=True)
# def set_correct_paths():
#     original_dir = os.getcwd()
#     os.chdir(os.path.join(original_dir, "image"))
#     yield
#     os.chdir(original_dir)


@pytest.fixture(scope="session", autouse=True)
def temp_pdf_file():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"in tests: {BASE_DIR}")
    DATA_DIR = os.path.join(BASE_DIR, "..", "image", "src", "data", "source")
    os.makedirs(DATA_DIR, exist_ok=True)

    math_filepath = os.path.join(DATA_DIR, "fake_math.pdf")
    family_filepath = os.path.join(DATA_DIR, "fake_family.pdf")


    # FPDF requires line-height as argument and call to set_font() before writing
    pdf1 = FPDF()
    pdf1.add_page()
    pdf1.set_font("Arial", size=12)
    pdf1.write(5, "3 + 4 = 8")
    pdf1.output(math_filepath)

    pdf2 = FPDF()
    pdf2.add_page()
    pdf2.set_font("Arial", size=12)
    pdf2.write(5, "I am Adel. My friend is Adit. His brother is Denis.")
    pdf2.output(family_filepath)

    yield

    os.remove(math_filepath)
    os.remove(family_filepath)


def test_fake_math():
    assert validate_query(
        question="What is 3+4? (Important: Answer with the number only)",
        expected_response="8"
    )


def test_tricky_question():
    assert validate_query(
        question="Who is Adit's brother? (Important: Answer with the name only)",
        expected_response="Denis"
    )

def test_negative():
    assert not validate_query(
        question="Who is Adit's sister? (Important: Answer with the name only)",
        expected_response="Denis"
    )


def validate_query(question: str, expected_response: str):
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)
    response = process_query(question)
    response_text = response.response_text
    # get only the answer without any template string
    only_response = response_text.split('\n---')[0].replace('Response: ', '').strip()
    prompt = EVAL_PROMPT.format(
        expected_response=expected_response,
        actual_response=only_response
    )

    llm = GoogleGenerativeAI(model="models/gemini-2.5-flash-preview-04-17")
    evaluation_result = llm.invoke(prompt).strip().lower()

    print(prompt)

    if "true" in evaluation_result:
        # Print response in Green if it is correct.
        print("\033[92m" + f"Response: {evaluation_result}" + "\033[0m")
        return True
    elif "false" in evaluation_result:
        # Print response in Red if it is incorrect.
        print("\033[91m" + f"Response: {evaluation_result}" + "\033[0m")
        return False
