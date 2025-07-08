from typing import List

import numpy as np
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity


def quick_search(documents: List[str], query: str, top_k: int = 10):
    """
    Perform a semantic search over a list of string documents using cosine similarity.

    Embeds the input documents and the query at runtime using a HuggingFace embedding model,
    computes cosine similarity between the query and document embeddings,
    and returns the top_k most similar documents.

    Args:
        documents (List[str]): A list of plain text documents to search through.
        query (str): The input query to compare against the documents.
        top_k (Optional[int]): The number of top similar documents to return (default is 10).

    Returns:
        List[str]: A list of the top_k most relevant documents sorted by similarity.
    """
    model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    document_embeddings = model.embed_documents(documents)
    query_embedding = model.embed_query(query)

    similarities = cosine_similarity([query_embedding], document_embeddings)[0]
    top_indices = np.argsort(-similarities)[:top_k]
    filtered = [documents[i] for i in top_indices]

    return filtered


def quick_faiss_search(
    documents: List[Document], query: str, top_k: int = 10
) -> List[Document]:
    """
    Perform a semantic search using FAISS vector store over a list of LangChain Documents using cosine similarity.

    Embeds the input documents and the query using a HuggingFace embedding model,
    computes cosine similarity between the query and document embeddings,
    and returns the top_k most similar documents.

    Args:
        documents (List[Document]): A list of LangChain Document objects to be indexed and searched.
        query (str): The input query to compare against the document index.
        top_k (Optional[int]): The number of top similar documents to return (default is 10).

    Returns:
        List[Document]: A list of the top_k most relevant documents sorted by similarity.
    """

    model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    db = FAISS.from_documents(
        documents=documents,
        embedding=model,
        distance_strategy=DistanceStrategy.COSINE,
    )
    results = db.similarity_search(query=query, k=top_k)

    return results
