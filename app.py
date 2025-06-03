from document_processing import load_documents, split_documents 
from chroma_handler import add_to_chroma
from query_handler import process_query
import argparse


def main():
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

    parser = argparse.ArgumentParser()
    parser.add_argument('query_text', type=str, help='The query text.')
    args = parser.parse_args()
    query_text = args.query_text
    process_query(query_text)


if __name__ == '__main__':
    main()
