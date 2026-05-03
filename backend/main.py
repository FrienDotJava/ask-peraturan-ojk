from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
from setup_agent import get_agent
import json

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
    source: str
    title: str
    page: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]


agent = get_agent()


def build_sources(result: dict) -> List[dict]:
    sources = []
    seen = set()

    for doc in result.get("retrieved_docs", []):
        key = (doc.metadata.get("source"), doc.metadata.get("page_label"))
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            "source": doc.metadata.get("source", ""),
            "title": doc.metadata.get("title", ""),
            "page": doc.metadata.get("page_label"),
        })

    for web in result.get("web_results") or []:
        sources.append({
            "source": web.get("url", ""),
            "title": web.get("title", ""),
            "page": None,
        })

    return sources


@app.post("/api/query", response_model=QueryResponse)
async def query(request: UserRequest):
    result = agent.invoke({"question": request.question})
    return QueryResponse(answer=result['answer'], sources=build_sources(result))


@app.post("/api/query/stream")
async def query_stream(request: UserRequest):
    async def event_stream():
        result = agent.invoke({"question": request.question})
        
        sources = build_sources(result)
        yield f"event: sources\ndata: {json.dumps(sources)}"

        from utils import init_model, load_config
        from context import get_full_prompt

        config = load_config()
        streaming_model = init_model(config["llm"], 0)

        context_parts = []
        for doc in result["retrieved_docs"]:
            source = doc.metadata.get("title")
            page = doc.metadata.get("page_label")
            context_parts.append(f"[Sumber: {source} | Halaman: {page}]\n{doc.page_content}")

        context = "\n\n---\n\n".join(context_parts)
        if result.get("web_results"):
            context += f"\n\nHasil Pencarian Web:\n{result['web_results']}"

        full_prompt = get_full_prompt(context, request.question)

        async for chunk in streaming_model.astream(full_prompt):
            token = chunk.content
            if token:
                yield f"event: token\ndata: {json.dumps(token)}\n\n"

        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok"}
