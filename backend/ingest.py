from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import time

load_dotenv()

class POJKMetadata(BaseModel):
    nomor: str = Field(description="Nomor POJK, misalnya '13 /POJK.05/2014'")
    tahun: str = Field(description="Tahun terbit peraturan, misalnya '2014'")
    topik: str = Field(description="Tentang apa peraturan tersebut, misalnya 'Penyelenggaraan Usaha Lembaga Keuangan Mikro'")


model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
extractor_model = model.with_structured_output(POJKMetadata)

def get_clean_title(first_page: str)->str:
    try:
        prompt = f"Ekstrak detail peraturan OJK dari halaman pertama dokumen berikut:\n\n{first_page[:1500]}"
        result = extractor_model.invoke(prompt)

        return f"POJK Nomor {result.nomor} Tahun {result.tahun} tentang {result.topik}"
    except Exception as e:
        print(f"Failed extracting title: {e}")
        return "Dokumen POJK Tidak Diketahui"

loaders = []
docs_path = Path("./docs")
for item in docs_path.iterdir():
    loaders.append(PyPDFLoader(str(item)))

docs = []
for loader in loaders:
    loaded_docs = loader.load()
    if not loaded_docs:
        continue

    first_page = loaded_docs[0].page_content
    clean_title = get_clean_title(first_page)
    print(f"File  : {Path(loader.file_path).name}")
    print(f"Judul : {clean_title}")
    print("-" * 50)

    for doc in loaded_docs:
        doc.metadata['title'] = clean_title

    docs.extend(loaded_docs)
    time.sleep(2)

legal_separators = [
    r"\nBAB\s+[IVXLCDM]+",
    r"\nBagian\s+[A-Za-z]+",
    r"\nPasal\s+\d+",
    r"\n\(\d+\)",
    r"\n[a-z]\.",
    r"\n\n", 
    r"\n",
    r" ",
    r""
]

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    separators=legal_separators,
    is_separator_regex=True,
    keep_separator=True
)

print("Splitting..")
chunks = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")

vector_store = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory="./chroma"
)

print(f"Indexed {len(chunks)} chunks")