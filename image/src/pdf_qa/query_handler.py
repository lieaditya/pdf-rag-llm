from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from .chroma_handler import get_chroma_db
from dataclasses import dataclass
from typing import List
from utils.api_key_loader import get_google_api_key


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


@dataclass
class QueryResponse:
    query_text: str
    response_text: str
    sources: List[str]


def process_query(query: str):
    """
    Processes a query using RAG with Gemini and ChromaDB.

    Paramters:
    query (str): The question you want to ask.

    Returns:
    QueryResponse: QueryResponse object containing the query, response, and its sources.
    """
    db = get_chroma_db()

    results = db.similarity_search_with_score(query, k=5)
    if len(results) == 0 or results[0][1] < 0.4:
        print("Unable to find matching results.")
        return

    context_str = '\n\n---\n\n'.join([doc.page_content for doc, _ in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_str, question=query)

    llm = GoogleGenerativeAI(
        model="models/gemini-2.5-flash-preview-04-17",
        google_api_key=get_google_api_key()
    )
    response_str = llm.invoke(prompt)
    sources = [doc.metadata.get('id', None) for doc, _ in results]

    response = f'Response: {response_str}\n---\nSources: {sources}'
    print(response)

    return QueryResponse(
        query_text=query,
        response_text=response_str,
        sources=sources
    )
