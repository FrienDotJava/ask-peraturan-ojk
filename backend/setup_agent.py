from langgraph.graph import StateGraph, END
from langchain_tavily import TavilySearch
from typing import TypedDict, List, Dict
from context import get_grade_prompt, get_full_prompt
from utils import load_config, init_retriever, init_model
from dotenv import load_dotenv

load_dotenv()

CONFIG = load_config()

_retriever = None
_model = None
_agent = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = init_retriever(CONFIG)
    return _retriever


def _get_model():
    global _model
    if _model is None:
        _model = init_model(CONFIG["llm"], 0, provider=CONFIG["provider"])
    return _model


class AgentState(TypedDict):
    question: str
    retrieved_docs: List
    web_results: List[Dict]
    answer: str
    needs_web: bool
    is_evaluate: bool


def retrieve_local(state: AgentState):
    docs = _get_retriever().invoke(state['question'])
    return {"retrieved_docs": docs}


def grade_documents(state: AgentState):
    doc_contents = [d.page_content for d in state["retrieved_docs"]]
    grade_prompt = get_grade_prompt(state["question"], doc_contents)
    grade = _get_model().invoke(grade_prompt).content.strip().lower()
    needs_web = "yes" not in grade
    return {"needs_web": needs_web}


def web_search(state: AgentState):
    if state["needs_web"]:
        web = TavilySearch(max_results=5)
        web_results = web.invoke({"query": state['question']})
        return {"web_results": web_results.get("results")}
    return {"web_results": ""}


def generate_answer(state: AgentState):
    context_parts = []
    for doc in state["retrieved_docs"]:
        source = doc.metadata.get("title")
        page = doc.metadata.get("page_label")
        context_parts.append(f"[Sumber: {source} | Halaman: {page}]\n{doc.page_content}")

    context = "\n\n---\n\n".join(context_parts)

    if state["web_results"]:
        web_contents = [result.get('content', "") for result in state['web_results']]
        formatted_web_results = "\n\n".join(web_contents)
        context += f"\n\nHasil Pencarian Web:\n{formatted_web_results}"

    full_prompt = get_full_prompt(context, state["question"], state.get("is_evaluate", False))
    answer = _get_model().invoke(full_prompt).content
    return {"answer": answer}


def get_agent():
    global _agent
    if _agent is None:
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

        _agent = workflow.compile()
    return _agent