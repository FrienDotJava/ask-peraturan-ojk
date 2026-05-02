from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
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
from context import SYSTEM_PROMPT, get_grade_prompt, get_full_prompt

load_dotenv()

app = FastAPI()

cors_origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

class UserRequest(BaseModel):
    question: str


class Source(BaseModel):
    title: str
    page: int


class ModelResponse(BaseModel):
    answer: str
    sources: List[Source]


embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
vector_store = Chroma(persist_directory="./chroma", embedding_function=embeddings)

chroma_data = vector_store.get()
chunks = [
    Document(page_content=text, metadata=meta)
    for text, meta in zip(chroma_data["documents"], chroma_data["metadatas"])
]

retriever = vector_store.as_retriever(kwargs={'k': 6})
bm25_retriever = BM25Retriever.from_documents(chunks, )

ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, retriever], weights=[0.5, 0.5])

reranker_model = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
reranker = CrossEncoderReranker(model=reranker_model, top_n=3)

final_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=ensemble_retriever
)

# model = init_chat_model(model="llama-3.3-70b-versatile", temperature=0, model_provider="groq")
model = init_chat_model(model="mistral-large-2512", temperature=0)

class AgentState(TypedDict):
    question: str
    retrieved_docs: List
    web_results: str
    answer: str
    needs_web: bool


def retrieve_local(state: AgentState):
    docs = final_retriever.invoke(state['question'])
    return {"retrieved_docs": docs}


def grade_documents(state: AgentState):
    doc_contents = [d.page_content for d in state["retrieved_docs"]]
    grade_prompt = get_grade_prompt(state["question"], doc_contents)
    grade = model.invoke(grade_prompt).content.strip().lower()
    needs_web = "yes" not in grade # if "yes", no need for web search
    return {"needs_web": needs_web}


def web_search(state: AgentState):
    if state["needs_web"]:
        web = TavilySearchResults(k=3)
        results = web.invoke(state['question'])
        return {"web_results": results}
    return {"web_results": ""}


def generate_answer(state: AgentState):
    context_parts = []
    for doc in state["retrieved_docs"]:
        source = doc.metadata.get("title")
        page = doc.metadata.get("page_label")
        context_parts.append(f"[Sumber: {source} | Halaman: {page}]\n{doc.page_content}")

    context = "\n\n---\n\n".join(context_parts)

    if state["web_results"]:
        context += f"\n\nHasil Pencarian Web:\n{state['web_results']}"
    full_prompt = get_full_prompt(context, state["question"])

    answer = model.invoke(full_prompt).content
    return {"answer": answer}


workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_local)
workflow.add_node("grade", grade_documents)
workflow.add_node("web_search", web_search)
workflow.add_node("generate", generate_answer)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade")
workflow.add_edge("grade", "web_search")
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

agent = workflow.compile()
