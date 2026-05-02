import yaml
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

def load_config(param_path: str = "config.yaml") -> dict:
    try:
        with open(param_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        raise Exception(f"Error loading file: {e}")
    

def init_retriever(config):
    embeddings = HuggingFaceEmbeddings(model_name=config["embedding_model"])
    vector_store = Chroma(persist_directory="./chroma", embedding_function=embeddings)

    chroma_data = vector_store.get()
    chunks = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(chroma_data["documents"], chroma_data["metadatas"])
    ]

    retriever = vector_store.as_retriever(kwargs={'k': 6})
    bm25_retriever = BM25Retriever.from_documents(chunks, )

    ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, retriever], weights=[0.5, 0.5])

    reranker_model = HuggingFaceCrossEncoder(model_name=config["reranker_model"])
    reranker = CrossEncoderReranker(model=reranker_model, top_n=3)

    return ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=ensemble_retriever
    )


def init_model(model, temp):
    return init_chat_model(model=model, temperature=temp)