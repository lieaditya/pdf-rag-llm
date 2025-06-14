from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from .chroma_handler import get_chroma_db, get_runtime_chroma_path
from dataclasses import dataclass
from typing import List
from utils.api_key_loader import get_google_api_key
import os


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


@dataclass(frozen=True)
class Source:
    filename: str
    page: int


@dataclass
class QueryResponse:
    query_text: str
    response_text: str
    sources: List[Source]


def process_query(query: str, user_id: str = "nobody") -> QueryResponse | None:
    """
    Processes a query using RAG with Gemini and ChromaDB.

    Paramters:
    query (str): The question you want to ask.
    user_id (str, optional): The identifier of the user making the query. Defaults to "nobody".

    Returns:
    QueryResponse | None: QueryResponse object containing the query, response, and its sources, or None if no suitable response is available.
    """
    db_path = get_runtime_chroma_path(user_id)
    if not os.path.isdir(db_path):
        print("Please upload some PDFs first")
        return None

    db = get_chroma_db(user_id)
    results = db.similarity_search_with_score(query, k=5)
    print(f"Results = {results[:3]}")
    if len(results) == 0 or results[0][1] < 0.4:
        print("Unable to find matching results.")
        return None

    context_str = '\n\n---\n\n'.join([doc.page_content for doc, _ in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_str, question=query)

    llm = GoogleGenerativeAI(
        model="models/gemini-2.5-flash-preview-04-17",
        google_api_key=get_google_api_key()
    )
    response_str = llm.invoke(prompt)

    sources = [
        str(doc.metadata.get('id'))
        for doc, score in results
        if 'id' in doc.metadata and score >= 0.95
    ]
    unique_sources = set()
    for source in sources:
        parts = source.split(':')
        filename = os.path.basename(parts[0])
        page = int(parts[1])
        unique_sources.add(Source(filename=filename, page=page))

    response = f'Response: {response_str}\n---\nSources: {sources}'
    print(response)

    return QueryResponse(
        query_text=query,
        response_text=response_str,
        sources=list(unique_sources)
    )
