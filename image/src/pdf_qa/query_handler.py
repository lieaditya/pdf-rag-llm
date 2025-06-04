from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from .embedding import generate_embedding


DB_PATH='src/data/chroma/'

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def process_query(query: str):
    """
    Processes a query using RAG with Gemini and ChromaDB.

    Paramters:
    query (str): The question you want to ask.

    Returns:
    str: The answer to your question based on the documents stored in the database as well as the sources to those answers. 
    """
    embeddings = generate_embedding()
    db = Chroma(
        collection_name='chunks',
        embedding_function=embeddings,
        persist_directory=DB_PATH
    )

    results = db.similarity_search_with_score(query, k=5)
    if len(results) == 0 or results[0][1] < 0.4:
        print("Unable to find matching results.")
        return

    context_str = '\n\n---\n\n'.join([doc.page_content for doc, _ in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_str, question=query)

    llm = GoogleGenerativeAI(model="models/gemini-2.5-flash-preview-04-17")
    response_str = llm.invoke(prompt)
    sources = [doc.metadata.get('id', None) for doc, _ in results]

    response = f'Response: {response_str}\n---\nSources: {sources}'
    print(response)

    return response
