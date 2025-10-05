from fastapi.testclient import TestClient
import pytest

from backend.main import app
from backend.services.bible_api import bible_api_service
from backend.models.schemas import BibleVersion, SearchResult, VerseContent


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_bibles_mocked(client, monkeypatch):
    def fake_get_bibles():
        return [
            BibleVersion(id="eng-ESV", name="English Standard Version", language="English", abbreviation="ESV"),
            BibleVersion(id="eng-KJV", name="King James Version", language="English", abbreviation="KJV"),
        ]

    monkeypatch.setattr(bible_api_service, "get_english_bibles", fake_get_bibles)

    resp = client.get("/api/v1/bibles")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["id"] == "eng-ESV"


def test_search_verses_mocked(client, monkeypatch):
    def fake_search(query: str, bible_id: str | None = None, limit: int = 10):
        return [
            SearchResult(
                verse=VerseContent(id="GEN.1.1", reference="Genesis 1:1", content="In the beginning..."),
                bible_id=bible_id or "eng-ESV",
                bible_name="English Standard Version",
            )
        ]

    monkeypatch.setattr(bible_api_service, "search_verses", fake_search)

    resp = client.post("/api/v1/search", json={"query": "beginning"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["verse"]["reference"] == "Genesis 1:1"


def test_get_verse_mocked(client, monkeypatch):
    def fake_get_verse(verse_id: str, bible_id: str):
        return VerseContent(id=verse_id, reference="John 3:16", content="For God so loved the world...")

    monkeypatch.setattr(bible_api_service, "get_verse", fake_get_verse)

    resp = client.get("/api/v1/verses/XYZ?bible_id=eng-ESV")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reference"] == "John 3:16"
