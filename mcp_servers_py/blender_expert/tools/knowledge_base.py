## Script for generating a vector database for Blender commands
import os
from typing import List, Dict
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from pydantic import SecretStr


from langchain_core.documents import Document
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter


# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI embeddings model
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=SecretStr(openai_api_key),
)

def query_vector_db_codebase(query: str) -> str:
    """
    Queries the vector database for Blender codebase and returns the results.
    Returns:
        str: The results of the query.
    """
    vector_store = Chroma(
        collection_name="blender_codebase",
        embedding_function=embeddings,
        persist_directory="vector_db/blender_codebase",
    )
    results = vector_store.similarity_search(query, k=5)
    return "\n".join([doc.page_content for doc in results])




def query_vector_db_manual(query: str) -> str:
    """
    Queries the vector database for Blender manual and returns the results.
    Returns:
        str: The results of the query.
    """
    vector_store = Chroma(
        collection_name="blender_manual",
        embedding_function=embeddings,
        persist_directory="vector_db/blender_manual",
    )
    results = vector_store.similarity_search(query, k=5)
    return "\n".join([doc.page_content for doc in results])



def fetch_online_documentation(query: str) -> str:
    """
    Fetches online documentation for Blender based on the query.
    Returns:
        str: The fetched documentation content.
    """
    # Placeholder for actual online documentation fetching logic
    # This could involve web scraping or API calls to Blender's official documentation
    return f"Online documentation content for query: {query}"
