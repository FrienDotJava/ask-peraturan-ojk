from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

loaders = []
docs_path = Path("./docs")
for item in docs_path.iterdir():
    loaders.append(PyPDFLoader(docs_path.name+ "/" +item.name))

docs = []
for loader in loaders:
    docs.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n", "\n\n", " ", ""]
)

chunks = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")

vector_store = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory="./chroma"
)

print(f"Indexed {len(chunks)} chunks")