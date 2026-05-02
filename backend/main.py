from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
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
    title: str
    page: int


class ModelResponse(BaseModel):
    answer: str
    sources: List[Source]


agent = get_agent()
