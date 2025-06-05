from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

# async def load_pages():
#     loader = PyPDFLoader(
#         "mcp_server/vector_databases/census_dhc_dp_techdoc/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf"
#     )
#     pages = []
#     async for page in loader.alazy_load():
#         pages.append(page)

#     return pages


# pages = asyncio.run(load_pages())


def load_pages():
    loader = PyPDFLoader(
        "mcp_server/vector_databases/census_dhc_dp_techdoc/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf"
    )
    pages = []
    for page in loader.load():
        pages.append(page)

    return pages


pages = load_pages()


print("Vectorizing census documentation... This may take a few minutes")
vector_store = InMemoryVectorStore.from_documents(
    pages, HuggingFaceEmbeddings(model_name="thenlper/gte-small")
)
