from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
from setup_agent import get_agent

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


@app.post("/api/query", response_model=QueryResponse)
async def query(request: UserRequest):
    result = agent.invoke({"question": request.question})
    retrieved_docs = result['retrieved_docs']
    web_results = result.get("web_results")

    sources = []
    for doc in retrieved_docs:
        source = doc.metadata.get('source')
        title = doc.metadata.get('title')
        page = doc.metadata.get('page_label')
        sources.append(Source(
            source=source,
            title=title,
            page=page
        ))
    if web_results:
        for web_result in web_results:
            sources.append(Source(
                source=web_result.get("url"),
                title=web_result.get("title")
            ))
    
    return QueryResponse(answer=result['answer'], sources=sources)


@app.get("/health")
async def health():
    return {"status": "ok"}
