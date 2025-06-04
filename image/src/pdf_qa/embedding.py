from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os


load_dotenv(override=False)
google_api_key = os.getenv("GOOGLE_API_KEY")


def generate_embedding():
    """
    Generates an embedding using the Google Generative AI model.

    Note:
    This function assumes that the `GoogleGenerativeAIEmbeddings` class is available and properly configure to connect to the Google AI services.

    Returns:
    embeddings: An instance of the GoogleGenerativeAIEmbeddings class.
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=google_api_key
    )
    return embeddings
