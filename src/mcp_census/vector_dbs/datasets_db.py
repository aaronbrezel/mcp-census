import os
from pathlib import Path
from typing import List, Optional

import httpx
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings
from mcp.server.fastmcp.utilities.logging import get_logger

LOG = get_logger(__name__)

PERSIST_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent / "census_datasets_faiss_index"
)


def fetch_census_dataset_documents() -> List[Document]:
    """
    Fetches the list of dataset metadata from the U.S. Census Bureau API
    and converts each dataset entry into a LangChain Document object.

    Returns:
        List[Document]: A list of LangChain Document instances containing
                        formatted dataset content and associated metadata.
    """
    # Fetch the list of available Census Datasets ~1,700 in totl
    LOG.info("Fetching Census datasets...")
    url = "https://api.census.gov/data.json"
    response = httpx.get(url)
    response.raise_for_status()
    data = response.json().get("dataset", [])

    # Construct LangChain Documents from the datasets
    documents: List[Document] = []
    for dataset in data:
        vintage = dataset.get("c_vintage", "Unknown Vintage")
        title = dataset.get("title", "No Title")
        description = dataset.get("description", "No Description")

        api_base_url = dataset.get("distribution", [])[0].get(
            "accessURL", "No API Base URL"
        )
        dataset["apiBaseURL"] = (
            api_base_url  # Add API base URL to metadata for easier filtering
        )
        key = "/".join(dataset.get("c_dataset", []))
        dataset["key"] = key  # Add dataset name to metadata for easier filtering

        documents.append(
            Document(
                page_content=f"Vintage: {vintage}\nDataset: {key}\nAPI base URL: {api_base_url}\nTitle: {title}\nDescription: {description}",
                metadata=dataset,
            )
        )

    return documents


def create_vectordb(documents: List[Document]) -> FAISS:
    """
    Creates a FAISS-based vector database from a list of LangChain Documents
    using HuggingFace sentence embeddings.

    Args:
        documents (List[Document]): A list of LangChain Documents to embed and index.

    Returns:
        FAISS: A FAISS vector store initialized with embedded document vectors.
    """
    # Create a vector store using pre-trained embedding model
    LOG.info("Embedding Census Dataset database... This could take a few minutes")
    model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(
        documents=documents,
        embedding=model,
        distance_strategy=DistanceStrategy.COSINE,
    )
    LOG.info("Done! Vector database created with", len(documents), "datasets.")

    return vectordb


def save_vectordb(vectordb: FAISS, persist_path: str = PERSIST_DIR):
    """
    Persists the FAISS vector store to local disk.

    Args:
        vectordb (FAISS): The vector database to save.
        persist_path (str, optional): Path to the directory where the index should be stored.
                                      Defaults to PERSIST_DIR.
    """
    vectordb.save_local(folder_path=persist_path)


def load_or_create_vectordb() -> FAISS:
    """
    Loads a previously saved FAISS vector store from disk. If none exists,
    it creates a new vector store from the Census datasets and saves it.

    Returns:
        FAISS: A loaded or newly created FAISS vector store instance.
    """
    if os.path.exists(PERSIST_DIR):
        LOG.info(f"Loading existing vector DB from '{PERSIST_DIR}'")
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectordb = FAISS.load_local(
            folder_path=PERSIST_DIR,
            embeddings=embedding,
            allow_dangerous_deserialization=True,
        )
    else:
        LOG.info("No saved vector DB found. Creating one now...")
        documents = fetch_census_dataset_documents()
        vectordb = create_vectordb(documents)
        save_vectordb(vectordb)
        LOG.info("Saved vector DB.")
    return vectordb


# Load on import
vectordb = load_or_create_vectordb()


def search_census_datasets(
    query: str,
    k: int = 5,
    vintage: Optional[int] = None,
    key: Optional[str] = None,
    api_base_url: Optional[str] = None,
    vectordb: FAISS = vectordb,
) -> List[str]:
    """
    Searches the vector DB using semantic similarity and optional metadata filtering.

    Args:
        query (str): Query string.
        k (int): Number of results.
        vintage (int): Optional vintage filter (e.g., 2020).
        key (str): Optional dataset name filter (e.g., 'dec/dp').
        api_base_url (str): Optional API base URL filter.
        vectordb (FAISS): The vector store instance.

    Returns:
        List[Document]: Matching documents.
    """
    metadata_filter = {}
    if vintage:
        metadata_filter["c_vintage"] = vintage
    if key:
        metadata_filter["key"] = key
    if api_base_url:
        metadata_filter["apiBaseURL"] = api_base_url

    results = vectordb.similarity_search(query=query, k=k, filter=metadata_filter)
    return [doc.page_content for doc in results]


# Rebuild on script run
if __name__ == "__main__":
    LOG.info("Rebuilding and saving the Census vector DB...")
    documents = fetch_census_dataset_documents()
    LOG.info(len(documents), "datasets fetched from Census API")
    vectordb = create_vectordb(documents)
    save_vectordb(vectordb)
    LOG.info("Done rebuilding. Vector DB saved to", PERSIST_DIR)
