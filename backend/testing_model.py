from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from dotenv import load_dotenv

load_dotenv()


embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
vector_store = Chroma(persist_directory="./chroma", embedding_function=embeddings)
retriever = vector_store.as_retriever(kwargs={'k': 4})

SYSTEM_PROMPT = """
Anda adalah asisten hukum yang ahli dalam peraturan Otoritas Jasa Keuangan Indonesia.
Jawab pertanyaan berikut HANYA berdasarkan konteks yang diberikan. 
Jika informasi tidak ada dalam konteks, katakan "Informasi tidak ditemukan dalam dokumen."
Selalu sebutkan sumber (Nama dokumen, pasal, dan ayat).

Konteks: 
{context}
"""

prompt = ChatPromptTemplate([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}")
])

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

question_answer_chain = create_stuff_documents_chain(model, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

response = rag_chain.invoke({"input": "Apa syarat dokumen untuk pinjam meminjam uang berbasis teknologi informasi?"})

print("=" * 60)
print("JAWABAN:")
print("=" * 60)
print(response["answer"])

print("\n" + "=" * 60)
print("SUMBER DOKUMEN:")
print("=" * 60)

for i, doc in enumerate(response["context"], 1):
    meta = doc.metadata
    print(f"\n[{i}] {meta.get('source', 'Unknown')}")
    print(f"    Halaman : {meta.get('page_label', meta.get('page', '-'))}")
    print(f"    Konten  : {doc.page_content[:300].strip()}...")
    print("-" * 60)