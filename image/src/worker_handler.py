from query_model import QueryModel
from pdf_qa.query_handler import process_query


def handler(event, context):
    query_item = QueryModel(**event)
    invoke_rag(query_item)


def invoke_rag(query_item: QueryModel):
    response = process_query(query_item.query_text)
    query_item.answer_text = response.response_text
    query_item.sources = response.sources
    query_item.is_complete = True
    query_item.put_item()
    print(f"Item is updated: {query_item}")
    return query_item


# ===== FOR LOCAL TESTING =====
def main():
    print("Running worker handler")
    query_item = QueryModel(
        query_text="rvalue"
    )
    response = invoke_rag(query_item)
    print(f"{response=}")


if __name__ == "__main__":
    main()
