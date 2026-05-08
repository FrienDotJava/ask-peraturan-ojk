from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    _faithfulness,
    _context_recall,
    _context_precision,
    _answer_correctness,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_huggingface import HuggingFaceEmbeddings
from utils import init_model, load_config
import json
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from ragas.run_config import RunConfig

with open('test_cases.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

dataset = Dataset.from_dict(data)

config = load_config()
llm = init_model(model=config['llm'], temp=0, provider=config['provider'])
# llm = ChatOllama(model="llama3.2")
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

embeddings = HuggingFaceEmbeddings(model="intfloat/multilingual-e5-large")

ragas_llm = LangchainLLMWrapper(llm)
ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)

# Inject per-metric using .llm and .embeddings attributes
_faithfulness.llm = ragas_llm
_context_recall.llm = ragas_llm
_context_precision.llm = ragas_llm
_answer_correctness.llm = ragas_llm
_answer_correctness.embeddings = ragas_embeddings

results = evaluate(
    dataset=dataset,
    metrics=[
        _faithfulness,
        _context_recall,
        _context_precision,
        _answer_correctness,
    ],
    llm=ragas_llm,
    embeddings=ragas_embeddings,
    run_config=RunConfig(
        max_workers=2,
        max_retries=5,
        timeout=60,
    )
)

print(results)
df = results.to_pandas()
df.to_csv("ragas_results.csv", index=False)
print(df[["user_input", "faithfulness", "context_precision", "context_recall", "answer_correctness"]])