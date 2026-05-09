import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from main import app


@pytest.fixture
def mock_agent():
    mock_doc = MagicMock()
    mock_doc.page_content = "Fintech P2P harus terdaftar OJK."
    mock_doc.metadata = {
        "source": "ojk_fintech.pdf",
        "title": "POJK 77/2016",
        "page_label": "5"
    }

    mock_result = {
        "answer": "Syarat fintech terdaftar OJK adalah...",
        "retrieved_docs": [mock_doc],
        "web_results": None
    }

    with patch("main.agent") as mock:
        mock.invoke.return_value = mock_result
        yield mock


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_query_returns_answer(mock_agent):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post("/api/query", json={"question": "Apa syarat fintech OJK?"})

    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0


@pytest.mark.asyncio
async def test_query_empty_question(mock_agent):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post("/api/query", json={"question": ""})

    assert res.status_code in [200, 422]


@pytest.mark.asyncio
async def test_sources_include_web_when_fallback():
    mock_doc = MagicMock()
    mock_doc.metadata = {"source": "ojk.pdf", "title": "OJK Doc", "page_label": "1"}

    mock_result = {
        "answer": "Berdasarkan pencarian web...",
        "retrieved_docs": [mock_doc],
        "web_results": [{"url": "https://ojk.go.id", "title": "OJK Website"}]
    }

    with patch("main.agent") as mock:
        mock.invoke.return_value = mock_result
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.post("/api/query", json={"question": "test"})

    data = res.json()
    sources = data["sources"]
    
    assert any(s["source"] == "https://ojk.go.id" for s in sources)