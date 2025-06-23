from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


def load_pages():
    pdf_path = (
        Path(__file__).resolve().parent.parent.parent.parent.parent.parent
        / "src"
        / "mcp_census"
        / "functions"
        / "vector_databases"
        / "census_dhc_dp_techdoc"
        / "2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf"
    )

    loader = PyPDFLoader(pdf_path)
    pages = []
    for page in loader.load():
        pages.append(page)

    return pages


pages = load_pages()


print("Vectorizing census documentation... This may take a few minutes")
vector_store = InMemoryVectorStore.from_documents(
    pages, HuggingFaceEmbeddings(model_name="thenlper/gte-small")
)
