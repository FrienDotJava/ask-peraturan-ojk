from langgraph.graph import StateGraph, END
from langchain_tavily import TavilySearchResults
from typing import TypedDict, List
from context import get_grade_prompt, get_full_prompt
from utils import load_config, init_retriever, init_model
from dotenv import load_dotenv

load_dotenv()

CONFIG = load_config()

FINAL_RETRIEVER = init_retriever(CONFIG)
MODEL = init_model(CONFIG["llm"], 0)

class AgentState(TypedDict):
    question: str
    retrieved_docs: List
    web_results: str
    answer: str
    needs_web: bool


def retrieve_local(state: AgentState):
    docs = FINAL_RETRIEVER.invoke(state['question'])
    return {"retrieved_docs": docs}


def grade_documents(state: AgentState):
    doc_contents = [d.page_content for d in state["retrieved_docs"]]
    grade_prompt = get_grade_prompt(state["question"], doc_contents)
    grade = MODEL.invoke(grade_prompt).content.strip().lower()
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

    answer = MODEL.invoke(full_prompt).content
    return {"answer": answer}

def get_agent():
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
    return agent