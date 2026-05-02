from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import TypedDict, List
from setup_agent import get_agent

load_dotenv()

# embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
# vector_store = Chroma(persist_directory="./chroma", embedding_function=embeddings)

# chroma_data = vector_store.get()
# chunks = [
#     Document(page_content=text, metadata=meta)
#     for text, meta in zip(chroma_data["documents"], chroma_data["metadatas"])
# ]

# retriever = vector_store.as_retriever(kwargs={'k': 6})
# bm25_retriever = BM25Retriever.from_documents(chunks, )

# ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, retriever], weights=[0.5, 0.5])

# reranker_model = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
# reranker = CrossEncoderReranker(model=reranker_model, top_n=3)

# final_retriever = ContextualCompressionRetriever(
#     base_compressor=reranker,
#     base_retriever=ensemble_retriever
# )

# # model = init_chat_model(model="llama-3.3-70b-versatile", temperature=0, model_provider="groq")
# model = init_chat_model(model="mistral-large-2512", temperature=0)

# class AgentState(TypedDict):
#     question: str
#     retrieved_docs: List
#     web_results: str
#     answer: str
#     needs_web: bool


# def retrieve_local(state: AgentState):
#     docs = final_retriever.invoke(state['question'])
#     return {"retrieved_docs": docs}


# def grade_documents(state: AgentState):
#     doc_contents = [d.page_content for d in state["retrieved_docs"]]
#     grade_prompt = f"""
# Pertanyaan: {state["question"]}
# Dokumen yang ditemukan: {doc_contents}

# Apakah dokumen ini cukup relevan untuk menjawab pertanyaan tersebut?
# Jawab HANYA dengan "yes" atau "no", tanpa penjelasan lain.
# """
#     grade = model.invoke(grade_prompt).content.strip().lower()
#     needs_web = "yes" not in grade # if "yes", no need for web search
#     return {"needs_web": needs_web}


# def web_search(state: AgentState):
#     if state["needs_web"]:
#         web = TavilySearchResults(k=3)
#         results = web.invoke(state['question'])
#         return {"web_results": results}
#     return {"web_results": ""}


# SYSTEM_PROMPT = """
# Anda adalah asisten hukum yang ahli dalam peraturan Otoritas Jasa Keuangan Indonesia.
# Jawab pertanyaan berikut HANYA berdasarkan konteks yang diberikan. 

# PENTING: Jika sebuah daftar (a, b, c, dst.) tampak tidak lengkap atau terpotong 
# di satu bagian konteks, cari kelanjutannya di bagian konteks lain yang diberikan.
# Gabungkan semua poin dari seluruh konteks sebelum menjawab.

# Jika informasi tidak ada dalam konteks, katakan "Informasi tidak ditemukan dalam dokumen."
# Selalu sebutkan sumber:
# - Nama dokumen (Contoh: PERATURAN OTORITAS JASA KEUANGAN NOMOR 13 /POJK.05/2014 Tentang Penyelenggaraan Usaha Lembaga Keuangan Mikro)
# - Pasal (Contoh: Pasal 1)
# - Poin/Ayat (Contoh: 1 atau (1))
# """

# def generate_answer(state: AgentState):
#     context_parts = []
#     for doc in state["retrieved_docs"]:
#         source = doc.metadata.get("title")
#         page = doc.metadata.get("page_label")
#         context_parts.append(f"[Sumber: {source} | Halaman: {page}]\n{doc.page_content}")

#     context = "\n\n---\n\n".join(context_parts)

#     if state["web_results"]:
#         context += f"\n\nHasil Pencarian Web:\n{state['web_results']}"

#     full_prompt = f"""{SYSTEM_PROMPT}

# Konteks:
# {context}

# Pertanyaan: {state["question"]}
# """

#     answer = model.invoke(full_prompt).content
#     return {"answer": answer}

# workflow = StateGraph(AgentState)
# workflow.add_node("retrieve", retrieve_local)
# workflow.add_node("grade", grade_documents)
# workflow.add_node("web_search", web_search)
# workflow.add_node("generate", generate_answer)

# workflow.set_entry_point("retrieve")
# workflow.add_edge("retrieve", "grade")
# workflow.add_edge("grade", "web_search")
# workflow.add_edge("web_search", "generate")
# workflow.add_edge("generate", END)

agent = get_agent()

def run_query(question: str):
    result = agent.invoke({"question": question})

    print("=" * 60)
    print("JAWABAN:")
    print("=" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("SUMBER DOKUMEN:")
    print("=" * 60)
    for i, doc in enumerate(result["retrieved_docs"], 1):
        meta = doc.metadata
        print(f"\n[{i}] {meta.get('source', 'Unknown')}")
        print(f"    Halaman : {meta.get('page_label')}")
        print(f"    Konten  : {doc.page_content[:300].strip()}...")
        print("-" * 60)

    web_results = result.get("web_results")
    if web_results:
        print("\n" + "=" * 60)
        print("HASIL WEB SEARCH:")
        print("=" * 60)
        for i, item in enumerate(web_results, 1):
            print(f"\n[{i}] {item.get('url', 'Unknown URL')}")
            print(f"    {item.get('content', '')[:300].strip()}...")
            print("-" * 60)
    
    web_used = "Ya" if web_results else "Tidak"
    print(f"\n[Web search digunakan: {web_used}]")
    print("-" * 60)


if __name__ == "__main__":
    run_query("Apa sanksi fintech yang tidak terdaftar OJK?")
    # run_query("Apa itu LKM?")