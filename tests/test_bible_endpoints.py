import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestBibleEndpoints:
    """Test Bible API endpoints."""
    
    @pytest.mark.api
    def test_get_bibles_success(self, client: TestClient, mock_successful_bible_api):
        """Test successful retrieval of Bible versions."""
        response = client.get("/api/v1/bibles")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["id"] == "eng-NIV"
        assert data[0]["name"] == "New International Version"
        assert data[0]["abbreviation"] == "NIV"
        
        # Verify the API service was called
        mock_successful_bible_api.get_english_bibles.assert_called_once()
    
    @pytest.mark.api
    def test_get_bibles_api_error(self, client: TestClient, mock_bible_api_service):
        """Test Bible versions endpoint when API service fails."""
        mock_bible_api_service.get_english_bibles.side_effect = Exception("API Error")
        
        response = client.get("/api/v1/bibles")
        
        # Should handle the error gracefully
        assert response.status_code == 500
    
    @pytest.mark.api
    def test_search_verses_success(self, client: TestClient, mock_successful_bible_api):
        """Test successful verse search."""
        search_data = {
            "query": "love",
            "bible_id": "eng-NIV",
            "limit": 10
        }
        
        response = client.post("/api/v1/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert "verse" in data[0]
        assert data[0]["verse"]["reference"] == "John 3:16"
        assert "bible_name" in data[0]
        
        # Verify the API service was called with correct parameters
        mock_successful_bible_api.search_verses.assert_called_once_with(
            query="love",
            bible_id="eng-NIV",
            limit=10
        )
    
    @pytest.mark.api
    def test_search_verses_no_query(self, client: TestClient):
        """Test verse search without query parameter."""
        search_data = {
            "bible_id": "eng-NIV",
            "limit": 10
        }
        
        response = client.post("/api/v1/search", json=search_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    def test_search_verses_empty_query(self, client: TestClient, mock_successful_bible_api):
        """Test verse search with empty query."""
        search_data = {
            "query": "",
            "bible_id": "eng-NIV",
            "limit": 10
        }
        
        response = client.post("/api/v1/search", json=search_data)
        
        # Should still process empty query
        assert response.status_code == 200
        mock_successful_bible_api.search_verses.assert_called_once_with(
            query="",
            bible_id="eng-NIV",
            limit=10
        )
    
    @pytest.mark.api
    def test_search_verses_default_limit(self, client: TestClient, mock_successful_bible_api):
        """Test verse search with default limit."""
        search_data = {
            "query": "peace",
            "bible_id": "eng-NIV"
        }
        
        response = client.post("/api/v1/search", json=search_data)
        
        assert response.status_code == 200
        mock_successful_bible_api.search_verses.assert_called_once_with(
            query="peace",
            bible_id="eng-NIV",
            limit=10  # Default limit
        )
    
    @pytest.mark.api
    def test_search_verses_no_bible_id(self, client: TestClient, mock_successful_bible_api):
        """Test verse search without bible_id."""
        search_data = {
            "query": "hope",
            "limit": 5
        }
        
        response = client.post("/api/v1/search", json=search_data)
        
        assert response.status_code == 200
        mock_successful_bible_api.search_verses.assert_called_once_with(
            query="hope",
            bible_id=None,
            limit=5
        )
    
    @pytest.mark.api
    def test_search_verses_api_error(self, client: TestClient, mock_bible_api_service):
        """Test verse search when API service fails."""
        mock_bible_api_service.search_verses.side_effect = Exception("Search API Error")
        
        search_data = {
            "query": "faith",
            "bible_id": "eng-NIV",
            "limit": 10
        }
        
        response = client.post("/api/v1/search", json=search_data)
        
        assert response.status_code == 500
    
    @pytest.mark.api
    def test_get_verse_success(self, client: TestClient, mock_successful_bible_api):
        """Test successful retrieval of a specific verse."""
        verse_id = "JHN.3.16"
        bible_id = "eng-NIV"
        
        response = client.get(f"/api/v1/verses/{verse_id}?bible_id={bible_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "verse" in data
        assert data["verse"]["reference"] == "John 3:16"
        
        mock_successful_bible_api.get_verse.assert_called_once_with(verse_id, bible_id)
    
    @pytest.mark.api
    def test_get_verse_not_found(self, client: TestClient, mock_bible_api_service):
        """Test verse retrieval when verse is not found."""
        mock_bible_api_service.get_verse.return_value = None
        
        verse_id = "NON.EXIST.1"
        bible_id = "eng-NIV"
        
        response = client.get(f"/api/v1/verses/{verse_id}?bible_id={bible_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Verse not found"
    
    @pytest.mark.api
    def test_get_verse_missing_bible_id(self, client: TestClient):
        """Test verse retrieval without bible_id parameter."""
        verse_id = "JHN.3.16"
        
        response = client.get(f"/api/v1/verses/{verse_id}")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    @pytest.mark.parametrize("query,bible_id,limit", [
        ("love", "eng-NIV", 5),
        ("peace", "eng-ESV", 15),
        ("hope", None, 10),
        ("John 3:16", "eng-NLT", 1),
        ("Psalm 23", "eng-NIV", 20)
    ])
    def test_search_verses_various_parameters(self, client, mock_successful_bible_api, query, bible_id, limit):
        """Test verse search with various parameter combinations."""
        search_data = {
            "query": query,
            "limit": limit
        }
        if bible_id:
            search_data["bible_id"] = bible_id
        
        response = client.post("/api/v1/search", json=search_data)
        
        assert response.status_code == 200
        mock_successful_bible_api.search_verses.assert_called_once_with(
            query=query,
            bible_id=bible_id,
            limit=limit
        )

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
