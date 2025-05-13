from langchain_google_genai import GoogleGenerativeAIEmbeddings

def generate_embedding():
    """
    Generates an embedding using the Google Generative AI model.

    Note:
    This function assumes that the `GoogleGenerativeAIEmbeddings` class is available and properly configure to connect to the Google AI services.

    Returns:
    embeddings: An instance of the GoogleGenerativeAIEmbeddings class.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-2.5-flash-preview-04-17")
    return embeddings
