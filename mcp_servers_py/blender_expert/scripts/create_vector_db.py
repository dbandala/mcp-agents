## Script for generating a vector database for Blender commands
import os
from typing import List, Dict
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
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

def create_vector_db_codebase() -> FAISS:
    """
    Loads documents from the specified directory, splits them, and creates a FAISS vector store.
    Returns:
        FAISS: The created FAISS vector store.
    """
    # Create an empty FAISS index which will be populated with documents
    vector_store = FAISS.from_texts(
        texts=["Initialization document"],
        embedding=embeddings,
    )
    
    # Set up a directory to save the FAISS index
    faiss_store_path = "vector_db/blender_codebase"
    # Create directory if it doesn't exist
    os.makedirs(faiss_store_path, exist_ok=True)

    file_extensions = [".cpp", ".cxx", ".cc", ".C", ".c++", ".h", ".hpp", ".py"]

    for ext in file_extensions:
        print(f"Processing files with extension: {ext}")
        # Load documents from the specified directory with the given file extension
        loader = DirectoryLoader(
            path="/Users/bandala/Documents/bandala/code/blender/source/blender",
            glob="**/*" + ext,
            loader_cls=TextLoader,
            recursive=True,
        )

        raw_docs = loader.load()
        print("*** raw docs: ", len(raw_docs))

        splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=100, length_function=len)
        docs = splitter.split_documents(raw_docs)

        print("*** split docs: ", len(docs))

        # Update metadata for each doc
        for doc in docs:
            doc.metadata = {
                "file_name": os.path.basename(doc.metadata.get("source", "")),
            }

        # Add documents to the vector store in batches
        batch_size = 128
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]
            # With FAISS, we need to create a new index and merge it with existing one
            new_index = FAISS.from_documents(batch, embeddings)
            vector_store.merge_from(new_index)
    
    # Save the FAISS index to disk
    vector_store.save_local("vector_db/blender_codebase")
    return vector_store


# create the vector database from a blender manual pdf
def create_vector_db_manual() -> FAISS:
    """
    Loads documents from the Blender manual PDF, splits them, and creates a FAISS vector store.
    Returns:
        FAISS: The created FAISS vector store.
    """
    # Create an empty FAISS index which will be populated with documents
    vector_store = FAISS.from_texts(
        texts=["Initialization document"],
        embedding=embeddings,
    )
    
    # Set up a directory to save the FAISS index
    faiss_store_path = "vector_db/blender_manual"
    # Create directory if it doesn't exist
    os.makedirs(faiss_store_path, exist_ok=True)

    # read pdf file
    pdf_path = "scripts/blender_python_reference_2_61_0.pdf"
    loader = PyPDFLoader(pdf_path)
    document = loader.load()

    # Split the document into smaller chunks for better processing
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=400)
    docs = text_splitter.split_documents(document)

    print("*** split docs: ", len(docs))

    # Add documents to the vector store in batches
    batch_size = 128
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        # With FAISS, we need to create a new index and merge it with existing one
        new_index = FAISS.from_documents(batch, embeddings)
        vector_store.merge_from(new_index)

    # Save the FAISS index to disk
    vector_store.save_local("vector_db/blender_manual")
    return vector_store



def create_vector_db_tutorials() -> FAISS:
    """
    Loads documents from the specified directory, splits them, and creates a FAISS vector store.
    Returns:
        FAISS: The created FAISS vector store.
    """
    # Create an empty FAISS index which will be populated with documents
    vector_store = FAISS.from_texts(
        texts=["Initialization document"],
        embedding=embeddings,
    )
    
    # Set up a directory to save the FAISS index
    faiss_store_path = "vector_db/blender_scripting_examples"
    # Create directory if it doesn't exist
    os.makedirs(faiss_store_path, exist_ok=True)

    file_extensions = [".cpp", ".cxx", ".cc", ".C", ".c++", ".h", ".hpp", ".py"]

    for dir in ["/Users/bandala/Documents/bandala/code/blender-scripting/scripts", "/Users/bandala/Documents/bandala/code/blender_plus_python"]:
        for ext in file_extensions:
            print(f"Processing files with extension: {ext}")
            # Load documents from the specified directory with the given file extension
            loader = DirectoryLoader(
                path=dir,
                glob="**/*" + ext,
                loader_cls=TextLoader,
                recursive=True,
            )

            raw_docs = loader.load()
            print("*** raw docs: ", len(raw_docs))

            splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=200, length_function=len)
            docs = splitter.split_documents(raw_docs)

            print("*** split docs: ", len(docs))

            # Update metadata for each doc
            for doc in docs:
                doc.metadata = {
                    "file_name": os.path.basename(doc.metadata.get("source", "")),
                }

            # Add documents to the vector store in batches
            batch_size = 128
            for i in range(0, len(docs), batch_size):
                batch = docs[i:i + batch_size]
                # With FAISS, we need to create a new index and merge it with existing one
                new_index = FAISS.from_documents(batch, embeddings)
                vector_store.merge_from(new_index)

    # Save the FAISS index to disk
    vector_store.save_local("vector_db/blender_scripting_examples")
    return vector_store



# query data
def query_vector_store(vector_store_path: str, query: str, top_k: int = 5) -> List[Dict]:
    """
    Query the vector store for similar documents based on the input query.
    
    Args:
        query (str): The query string to search for.
        top_k (int): The number of top results to return.
        
    Returns:
        List[Dict]: A list of dictionaries containing the document content and metadata.
    """
    # Load the FAISS index from disk
    try:
        vector_store = FAISS.load_local(
            vector_store_path,
            embeddings,
            allow_dangerous_deserialization=True,  # Set to True for loading existing vector store
        )
    except Exception as e:
        raise ValueError(f"Error loading vector store at {vector_store_path}: {str(e)}")

    if not vector_store:
        raise ValueError(f"Vector store at {vector_store_path} not found or is empty.")
    
    results = vector_store.similarity_search(query, k=top_k)
    return [{"content": doc.page_content, "metadata": doc.metadata} for doc in results]

# Example usage
if __name__ == "__main__":
    # Create the vector database for the Blender codebase
    #vector_store = create_vector_db_codebase()

    # Create the vector database for the Blender manual
    # vector_store_manual = create_vector_db_manual()

    # Create the vector database for Blender scripting examples
    vector_store_tutorials = create_vector_db_tutorials()

    db = [
        "vector_db/blender_codebase",
        "vector_db/blender_manual",
        "vector_db/blender_scripting_examples"
    ]


    query = "sphere mesh example script"
    results = query_vector_store(db[2], query)

    print(f"Query: {query}\n")
    print(f"Number of results found: {len(results)}\n")

    for result in results:
        print(f"Content: {result['content'][:400]}...")  # Print first 200 characters
        print(f"Metadata: {result['metadata']}\n\n")