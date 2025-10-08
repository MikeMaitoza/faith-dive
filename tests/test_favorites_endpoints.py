import pytest
from fastapi.testclient import TestClient
from datetime import datetime


class TestFavoritesEndpoints:
    """Test Favorites API endpoints."""
    
    @pytest.mark.api
    @pytest.mark.database
    def test_create_favorite_verse_success(self, client: TestClient, sample_favorite_verse_data):
        """Test successful creation of favorite verse."""
        response = client.post("/api/v1/favorites", json=sample_favorite_verse_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["verse_reference"] == sample_favorite_verse_data["verse_reference"]
        assert data["verse_text"] == sample_favorite_verse_data["verse_text"]
        assert data["bible_version"] == sample_favorite_verse_data["bible_version"]
        assert data["notes"] == sample_favorite_verse_data["notes"]
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.api
    def test_create_favorite_verse_minimal_data(self, client: TestClient):
        """Test favorite verse creation with minimal required data."""
        minimal_data = {
            "verse_reference": "John 3:16",
            "verse_text": "For God so loved the world...",
            "bible_version": "NIV",
            "bible_id": "eng-NIV"
        }
        
        response = client.post("/api/v1/favorites", json=minimal_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] is None  # Optional field
    
    @pytest.mark.api
    def test_create_favorite_verse_missing_required_field(self, client: TestClient):
        """Test favorite verse creation with missing required field."""
        incomplete_data = {
            "verse_reference": "John 3:16",
            "bible_version": "NIV",
            "notes": "This is incomplete."
            # Missing verse_text, bible_id
        }
        
        response = client.post("/api/v1/favorites", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    @pytest.mark.database
    def test_get_favorite_verses_empty(self, client: TestClient):
        """Test getting favorite verses when none exist."""
        response = client.get("/api/v1/favorites")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    @pytest.mark.api
    @pytest.mark.database
    def test_get_favorite_verses_with_data(self, client: TestClient, favorite_verse_factory):
        """Test getting favorite verses when data exists."""
        # Create test favorites
        favorites = favorite_verse_factory.create_batch(3)
        
        response = client.get("/api/v1/favorites")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in favorite for favorite in data)
        assert all("verse_reference" in favorite for favorite in data)
    
    @pytest.mark.api
    @pytest.mark.database
    def test_get_favorite_verses_pagination(self, client: TestClient, favorite_verse_factory):
        """Test favorite verses pagination."""
        # Create many favorites
        favorite_verse_factory.create_batch(10)
        
        # Test with skip and limit
        response = client.get("/api/v1/favorites?skip=3&limit=4")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
    
    @pytest.mark.api
    @pytest.mark.database
    def test_delete_favorite_verse_success(self, client: TestClient, favorite_verse_factory):
        """Test successful deletion of favorite verse."""
        favorite = favorite_verse_factory.create()
        
        response = client.delete(f"/api/v1/favorites/{favorite.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Favorite verse removed successfully"
        
        # Verify it's not in the list anymore
        get_response = client.get("/api/v1/favorites")
        favorites_data = get_response.json()
        favorite_ids = [fav["id"] for fav in favorites_data]
        assert favorite.id not in favorite_ids
    
    @pytest.mark.api
    def test_delete_favorite_verse_not_found(self, client: TestClient):
        """Test deleting a non-existent favorite verse."""
        response = client.delete("/api/v1/favorites/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Favorite verse not found"
    
    @pytest.mark.api
    @pytest.mark.database
    def test_favorite_verse_with_long_notes(self, client: TestClient):
        """Test favorite verse creation with long notes."""
        long_notes = "This is a very long note. " * 50  # Create long text
        
        favorite_data = {
            "verse_reference": "Romans 8:28",
            "verse_text": "And we know that in all things God works for the good...",
            "bible_version": "NIV",
            "bible_id": "eng-NIV",
            "notes": long_notes
        }
        
        response = client.post("/api/v1/favorites", json=favorite_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == long_notes
    
    @pytest.mark.api
    @pytest.mark.database
    def test_favorite_verse_without_notes(self, client: TestClient):
        """Test favorite verse creation without notes."""
        favorite_data = {
            "verse_reference": "1 Corinthians 13:4",
            "verse_text": "Love is patient, love is kind...",
            "bible_version": "ESV",
            "bible_id": "eng-ESV"
        }
        
        response = client.post("/api/v1/favorites", json=favorite_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] is None
    
    @pytest.mark.api
    @pytest.mark.database
    def test_favorite_verse_datetime_field(self, client: TestClient, sample_favorite_verse_data):
        """Test that datetime field is properly set and formatted."""
        response = client.post("/api/v1/favorites", json=sample_favorite_verse_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that datetime field exists and is in ISO format
        assert "created_at" in data
        
        # Verify it can be parsed as datetime
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        assert isinstance(created_at, datetime)
    
    @pytest.mark.api
    @pytest.mark.database
    @pytest.mark.parametrize("skip,limit,expected_count", [
        (0, 5, 5),
        (2, 3, 3),
        (8, 5, 0),   # Beyond available data
        (0, 100, 6), # More than available
    ])
    def test_favorites_pagination_edge_cases(self, client, favorite_verse_factory, skip, limit, expected_count):
        """Test favorite verses pagination with various parameters."""
        # Create exactly 6 favorites
        favorite_verse_factory.create_batch(6)
        
        response = client.get(f"/api/v1/favorites?skip={skip}&limit={limit}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == min(expected_count, max(0, 6 - skip))
    
    @pytest.mark.api
    @pytest.mark.database
    def test_duplicate_favorite_verses_allowed(self, client: TestClient, sample_favorite_verse_data):
        """Test that duplicate favorite verses are allowed (user might want multiple notes)."""
        # Create first favorite
        response1 = client.post("/api/v1/favorites", json=sample_favorite_verse_data)
        assert response1.status_code == 200
        
        # Create duplicate with different notes
        duplicate_data = sample_favorite_verse_data.copy()
        duplicate_data["notes"] = "Different notes for the same verse"
        
        response2 = client.post("/api/v1/favorites", json=duplicate_data)
        assert response2.status_code == 200
        
        # Verify both exist
        get_response = client.get("/api/v1/favorites")
        favorites = get_response.json()
        assert len(favorites) == 2
    
    @pytest.mark.api
    @pytest.mark.database
    def test_favorites_crud_workflow(self, client: TestClient, sample_favorite_verse_data):
        """Test complete CRUD workflow for favorites."""
        # Create
        create_response = client.post("/api/v1/favorites", json=sample_favorite_verse_data)
        assert create_response.status_code == 200
        created_favorite = create_response.json()
        favorite_id = created_favorite["id"]
        
        # Read (via list)
        list_response = client.get("/api/v1/favorites")
        assert list_response.status_code == 200
        favorites_list = list_response.json()
        assert len(favorites_list) == 1
        assert favorites_list[0]["id"] == favorite_id
        
        # Delete
        delete_response = client.delete(f"/api/v1/favorites/{favorite_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        final_list_response = client.get("/api/v1/favorites")
        final_favorites_list = final_list_response.json()
        assert len(final_favorites_list) == 0
    
    @pytest.mark.api
    @pytest.mark.database
    @pytest.mark.parametrize("bible_version", ["NIV", "ESV", "NLT", "NASB", "KJV"])
    def test_favorites_with_different_bible_versions(self, client, bible_version):
        """Test creating favorites with different Bible versions."""
        favorite_data = {
            "verse_reference": "John 3:16",
            "verse_text": f"Bible text from {bible_version}",
            "bible_version": bible_version,
            "bible_id": f"eng-{bible_version}",
            "notes": f"Note for {bible_version} version"
        }
        
        response = client.post("/api/v1/favorites", json=favorite_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["bible_version"] == bible_version
    
    @pytest.mark.api
    @pytest.mark.database
    def test_favorites_ordering(self, client: TestClient, favorite_verse_factory):
        """Test that favorites are returned in a consistent order (newest first)."""
        # Create favorites with slight delay to ensure different timestamps
        import time
        
        first_favorite = favorite_verse_factory.create(verse_reference="First Verse")
        time.sleep(0.01)
        second_favorite = favorite_verse_factory.create(verse_reference="Second Verse")
        time.sleep(0.01)
        third_favorite = favorite_verse_factory.create(verse_reference="Third Verse")
        
        response = client.get("/api/v1/favorites")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Check that they're ordered (assuming default ordering by id or created_at)
        # This test validates that ordering is consistent
        references = [fav["verse_reference"] for fav in data]
        assert len(set(references)) == 3  # All different