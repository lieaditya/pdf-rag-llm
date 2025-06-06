from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from utils.api_key_loader import get_google_api_key


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
        google_api_key=get_google_api_key()
    )
    return embeddings
