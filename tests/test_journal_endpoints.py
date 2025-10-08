import pytest
from fastapi.testclient import TestClient
from datetime import datetime


class TestJournalEndpoints:
    """Test Journal API endpoints."""
    
    @pytest.mark.api
    @pytest.mark.database
    def test_create_journal_entry_success(self, client: TestClient, sample_journal_entry_data):
        """Test successful creation of journal entry."""
        response = client.post("/api/v1/journal", json=sample_journal_entry_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["verse_reference"] == sample_journal_entry_data["verse_reference"]
        assert data["verse_text"] == sample_journal_entry_data["verse_text"]
        assert data["title"] == sample_journal_entry_data["title"]
        assert data["content"] == sample_journal_entry_data["content"]
        assert data["tags"] == sample_journal_entry_data["tags"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.api
    def test_create_journal_entry_minimal_data(self, client: TestClient):
        """Test journal entry creation with minimal required data."""
        minimal_data = {
            "verse_reference": "John 3:16",
            "verse_text": "For God so loved the world...",
            "bible_version": "NIV",
            "bible_id": "eng-NIV",
            "content": "This is a reflection."
        }
        
        response = client.post("/api/v1/journal", json=minimal_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] is None  # Optional field
        assert data["tags"] == []    # Default empty list
    
    @pytest.mark.api
    def test_create_journal_entry_missing_required_field(self, client: TestClient):
        """Test journal entry creation with missing required field."""
        incomplete_data = {
            "verse_reference": "John 3:16",
            "bible_version": "NIV",
            "content": "This is incomplete."
            # Missing verse_text, bible_id
        }
        
        response = client.post("/api/v1/journal", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    @pytest.mark.database
    def test_get_journal_entries_empty(self, client: TestClient):
        """Test getting journal entries when none exist."""
        response = client.get("/api/v1/journal")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    @pytest.mark.api
    @pytest.mark.database
    def test_get_journal_entries_with_data(self, client: TestClient, journal_entry_factory):
        """Test getting journal entries when data exists."""
        # Create test entries
        entries = journal_entry_factory.create_batch(5)
        
        response = client.get("/api/v1/journal")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert all("id" in entry for entry in data)
        assert all("verse_reference" in entry for entry in data)
    
    @pytest.mark.api
    @pytest.mark.database
    def test_get_journal_entries_pagination(self, client: TestClient, journal_entry_factory):
        """Test journal entries pagination."""
        # Create many entries
        journal_entry_factory.create_batch(15)
        
        # Test with skip and limit
        response = client.get("/api/v1/journal?skip=5&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
    
    @pytest.mark.api
    @pytest.mark.database
    def test_get_journal_entry_by_id_success(self, client: TestClient, journal_entry_factory):
        """Test getting a specific journal entry by ID."""
        entry = journal_entry_factory.create()
        
        response = client.get(f"/api/v1/journal/{entry.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry.id
        assert data["verse_reference"] == entry.verse_reference
    
    @pytest.mark.api
    def test_get_journal_entry_not_found(self, client: TestClient):
        """Test getting a non-existent journal entry."""
        response = client.get("/api/v1/journal/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Journal entry not found"
    
    @pytest.mark.api
    @pytest.mark.database
    def test_update_journal_entry_success(self, client: TestClient, journal_entry_factory):
        """Test successful update of journal entry."""
        entry = journal_entry_factory.create()
        
        update_data = {
            "title": "Updated Title",
            "content": "Updated content with new insights.",
            "tags": ["updated", "new"]
        }
        
        response = client.put(f"/api/v1/journal/{entry.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["tags"] == update_data["tags"]
        assert data["id"] == entry.id  # ID should remain the same
    
    @pytest.mark.api
    @pytest.mark.database
    def test_update_journal_entry_partial(self, client: TestClient, journal_entry_factory):
        """Test partial update of journal entry."""
        entry = journal_entry_factory.create(title="Original Title")
        original_content = entry.content
        
        # Only update title
        update_data = {"title": "New Title Only"}
        
        response = client.put(f"/api/v1/journal/{entry.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title Only"
        assert data["content"] == original_content  # Should remain unchanged
    
    @pytest.mark.api
    def test_update_journal_entry_not_found(self, client: TestClient):
        """Test updating a non-existent journal entry."""
        update_data = {"title": "New Title"}
        
        response = client.put("/api/v1/journal/99999", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Journal entry not found"
    
    @pytest.mark.api
    @pytest.mark.database
    def test_delete_journal_entry_success(self, client: TestClient, journal_entry_factory):
        """Test successful deletion of journal entry."""
        entry = journal_entry_factory.create()
        
        response = client.delete(f"/api/v1/journal/{entry.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Journal entry deleted successfully"
        
        # Verify entry is deleted
        get_response = client.get(f"/api/v1/journal/{entry.id}")
        assert get_response.status_code == 404
    
    @pytest.mark.api
    def test_delete_journal_entry_not_found(self, client: TestClient):
        """Test deleting a non-existent journal entry."""
        response = client.delete("/api/v1/journal/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Journal entry not found"
    
    @pytest.mark.api
    @pytest.mark.database
    def test_journal_entry_tags_handling(self, client: TestClient):
        """Test proper handling of tags in journal entries."""
        entry_data = {
            "verse_reference": "Psalm 23:1",
            "verse_text": "The Lord is my shepherd...",
            "bible_version": "NIV",
            "bible_id": "eng-NIV",
            "content": "Reflection on God's care.",
            "tags": ["shepherd", "care", "protection", "psalm"]
        }
        
        response = client.post("/api/v1/journal", json=entry_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tags"]) == 4
        assert "shepherd" in data["tags"]
    
    @pytest.mark.api
    @pytest.mark.database
    @pytest.mark.parametrize("skip,limit,expected_count", [
        (0, 5, 5),
        (3, 7, 7),
        (10, 5, 0),  # Beyond available data
        (0, 100, 8),  # More than available
    ])
    def test_journal_pagination_edge_cases(self, client, journal_entry_factory, skip, limit, expected_count):
        """Test journal entry pagination with various parameters."""
        # Create exactly 8 entries
        journal_entry_factory.create_batch(8)
        
        response = client.get(f"/api/v1/journal?skip={skip}&limit={limit}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == min(expected_count, max(0, 8 - skip))
    
    @pytest.mark.api
    @pytest.mark.database
    def test_journal_entry_datetime_fields(self, client: TestClient, sample_journal_entry_data):
        """Test that datetime fields are properly set and formatted."""
        response = client.post("/api/v1/journal", json=sample_journal_entry_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that datetime fields exist and are in ISO format
        assert "created_at" in data
        assert "updated_at" in data
        
        # Verify they can be parsed as datetime
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        
        assert isinstance(created_at, datetime)
        assert isinstance(updated_at, datetime)
        assert created_at <= updated_at
    
    @pytest.mark.api
    @pytest.mark.database
    def test_journal_crud_workflow(self, client: TestClient, sample_journal_entry_data):
        """Test complete CRUD workflow for journal entries."""
        # Create
        create_response = client.post("/api/v1/journal", json=sample_journal_entry_data)
        assert create_response.status_code == 200
        created_entry = create_response.json()
        entry_id = created_entry["id"]
        
        # Read
        read_response = client.get(f"/api/v1/journal/{entry_id}")
        assert read_response.status_code == 200
        read_entry = read_response.json()
        assert read_entry["content"] == sample_journal_entry_data["content"]
        
        # Update
        update_data = {"title": "Updated in workflow test"}
        update_response = client.put(f"/api/v1/journal/{entry_id}", json=update_data)
        assert update_response.status_code == 200
        updated_entry = update_response.json()
        assert updated_entry["title"] == "Updated in workflow test"
        
        # Delete
        delete_response = client.delete(f"/api/v1/journal/{entry_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        final_read_response = client.get(f"/api/v1/journal/{entry_id}")
        assert final_read_response.status_code == 404

from contextlib import contextmanager
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.connection import get_db
from backend.models.database import Base, JournalEntry


@pytest.fixture()
def db_session() -> Generator:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create schema
    Base.metadata.create_all(bind=engine)

    @contextmanager
    def _session_scope() -> Generator:
        db = TestingSessionLocal()
        try:
            yield db
            db.commit()
        finally:
            db.close()

    yield _session_scope


@pytest.fixture()
def client(db_session):
    # Override FastAPI dependency to use the in-memory DB
    def override_get_db():
        with db_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_journal_crud_flow(client):
    # Create
    payload = {
        "verse_reference": "John 3:16",
        "verse_text": "For God so loved the world...",
        "bible_version": "ESV",
        "bible_id": "eng-ESV",
        "title": "My note",
        "content": "Reflection",
        "tags": ["love", "gospel"],
    }
    resp = client.post("/api/v1/journal", json=payload)
    assert resp.status_code == 200
    created = resp.json()
    assert created["id"] > 0

    entry_id = created["id"]

    # List
    resp = client.get("/api/v1/journal")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1

    # Get
    resp = client.get(f"/api/v1/journal/{entry_id}")
    assert resp.status_code == 200
    item = resp.json()
    assert item["title"] == "My note"

    # Update
    resp = client.put(
        f"/api/v1/journal/{entry_id}", json={"title": "Updated", "tags": ["updated"]}
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["title"] == "Updated"
    assert updated["tags"] == ["updated"]

    # Delete
    resp = client.delete(f"/api/v1/journal/{entry_id}")
    assert resp.status_code == 200

    # Verify empty
    resp = client.get("/api/v1/journal")
    assert resp.status_code == 200
    assert resp.json() == []
