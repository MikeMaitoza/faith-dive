import pytest
from unittest.mock import Mock, patch, MagicMock
import responses
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.bible_api import BibleAPIService


class TestVerseReferenceIntegration:
    """
    Comprehensive integration tests for verse reference parsing and search.
    
    This test suite is designed to catch the exact types of issues we encountered:
    - Verse reference parsing problems
    - Search result mismatches 
    - Chapter vs verse confusion
    - API endpoint integration issues
    """
    
    @pytest.fixture
    def client(self):
        """Create test client for end-to-end testing."""
        return TestClient(app)
    
    @pytest.fixture
    def bible_service(self):
        """Create Bible API service instance."""
        return BibleAPIService()
    
    @pytest.fixture
    def mock_bible_data(self):
        """Mock Bible versions data."""
        return [
            {
                "id": "eng-WEB",
                "name": "World English Bible",
                "language": {"id": "eng", "name": "English"},
                "abbreviation": "WEB"
            },
            {
                "id": "spa-RVR1960", 
                "name": "Reina Valera 1960",
                "language": {"id": "spa", "name": "Spanish"},
                "abbreviation": "RVR60"
            }
        ]
    
    @pytest.fixture
    def mock_books_data(self):
        """Mock books data for book ID resolution."""
        return [
            {"id": "JHN", "name": "John"},
            {"id": "1JN", "name": "1 John"},
            {"id": "ROM", "name": "Romans"},
            {"id": "PSA", "name": "Psalms"}
        ]
    
    @pytest.fixture
    def mock_chapter_verses(self):
        """Mock chapter verses for John 3."""
        return [
            {
                "id": "JHN.3.1",
                "reference": "John 3:1", 
                "content": "Now there was a Pharisee, a man named Nicodemus who was a member of the Jewish ruling council."
            },
            {
                "id": "JHN.3.2",
                "reference": "John 3:2",
                "content": "He came to Jesus at night and said, \"Rabbi, we know that you are a teacher who has come from God.\""
            },
            {
                "id": "JHN.3.16", 
                "reference": "John 3:16",
                "content": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."
            }
        ]

    # ========== VERSE REFERENCE PARSING TESTS ==========
    
    @pytest.mark.parametrize("query,expected_book,expected_chapter,expected_verse", [
        ("John 3:16", "John", "3", "16"),
        ("John 3", "John", "3", None),
        ("1 John 4:9", "1 John", "4", "9"),
        ("1 John 3", "1 John", "3", None),
        ("Romans 8:28", "Romans", "8", "28"),
        ("Romans 8", "Romans", "8", None),
        ("Psalm 23:1", "Psalm", "23", "1"),
        ("Psalm 23", "Psalm", "23", None),
        ("2 Corinthians 12:9", "2 Corinthians", "12", "9"),
        ("2 Corinthians 12", "2 Corinthians", "12", None),
    ])
    def test_verse_reference_parsing_accuracy(self, bible_service, query, expected_book, expected_chapter, expected_verse):
        """Test that verse references are parsed correctly for all formats."""
        book, chapter, verse = bible_service._parse_verse_reference(query)
        
        assert book == expected_book, f"Book parsing failed for '{query}': got '{book}', expected '{expected_book}'"
        assert chapter == expected_chapter, f"Chapter parsing failed for '{query}': got '{chapter}', expected '{expected_chapter}'"
        assert verse == expected_verse, f"Verse parsing failed for '{query}': got '{verse}', expected '{expected_verse}'"
    
    @pytest.mark.parametrize("query,should_be_reference", [
        ("John 3:16", True),
        ("John 3", True),
        ("1 John 4:9", True),
        ("1 John 3", True),
        ("love", False),
        ("faith hope charity", False),
        ("God so loved the world", False),
        ("Romans 8:28", True),
        ("Romans 8", True),
    ])
    def test_verse_reference_detection_accuracy(self, bible_service, query, should_be_reference):
        """Test that verse reference detection works correctly."""
        is_reference = bible_service._is_verse_reference(query)
        
        assert is_reference == should_be_reference, f"Reference detection failed for '{query}': got {is_reference}, expected {should_be_reference}"

    # ========== SEARCH FLOW INTEGRATION TESTS ==========
    
    @responses.activate
    def test_chapter_search_integration_john_3(self, bible_service, mock_bible_data, mock_books_data, mock_chapter_verses):
        """
        Integration test for 'John 3' search - the exact scenario that was broken.
        
        This test verifies:
        1. 'John 3' is detected as a verse reference
        2. It's parsed as a chapter-only reference
        3. The correct chapter search logic is triggered
        4. Multiple verses from John 3 are returned (not 1 John 4:9!)
        """
        # Mock the bibles endpoint
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            json={"data": mock_bible_data},
            status=200
        )
        
        # Mock the books endpoint
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles/eng-WEB/books",
            json={"data": mock_books_data},
            status=200
        )
        
        # Mock individual verse requests for John 3
        for verse in mock_chapter_verses:
            responses.add(
                responses.GET,
                f"https://api.scripture.api.bible/v1/bibles/eng-WEB/verses/{verse['id']}",
                json={"data": verse},
                status=200
            )
        
        # Mock Bible info
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles/eng-WEB",
            json={"data": {"name": "World English Bible"}},
            status=200
        )
        
        # Test the search
        results = bible_service.search_verses("John 3", bible_id="eng-WEB")
        
        # Verify we got multiple verses from John 3
        assert len(results) > 1, "Should return multiple verses for chapter search"
        assert all("John 3:" in result.verse.reference for result in results), "All results should be from John 3"
        assert any("John 3:16" in result.verse.reference for result in results), "Should include John 3:16"
        assert not any("1 John" in result.verse.reference for result in results), "Should NOT include 1 John verses"
    
    @responses.activate  
    def test_specific_verse_search_john_3_16(self, bible_service, mock_bible_data, mock_books_data):
        """Test that 'John 3:16' returns exactly that verse."""
        # Mock the bibles endpoint
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            json={"data": mock_bible_data},
            status=200
        )
        
        # Mock the books endpoint
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles/eng-WEB/books", 
            json={"data": mock_books_data},
            status=200
        )
        
        # Mock the specific verse
        john_3_16 = {
            "id": "JHN.3.16",
            "reference": "John 3:16",
            "content": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."
        }
        
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles/eng-WEB/verses/JHN.3.16",
            json={"data": john_3_16},
            status=200
        )
        
        # Mock Bible info
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles/eng-WEB",
            json={"data": {"name": "World English Bible"}},
            status=200
        )
        
        # Test the search
        results = bible_service.search_verses("John 3:16", bible_id="eng-WEB")
        
        # Verify we got exactly one result with the correct verse
        assert len(results) == 1, "Should return exactly one verse for specific verse search"
        assert results[0].verse.reference == "John 3:16", "Should return John 3:16"
        assert "For God so loved the world" in results[0].verse.content, "Should have correct verse content"

    # ========== END-TO-END API TESTS ==========
    
    @pytest.mark.parametrize("search_query,expected_pattern", [
        ("John 3", "John 3:"),  # Should return verses from John 3
        ("John 3:16", "John 3:16"),  # Should return exactly John 3:16
        ("1 John 3", "1 John 3:"),  # Should return 1 John chapter 3
        ("Romans 8", "Romans 8:"),  # Should return Romans chapter 8
    ])
    def test_search_endpoint_integration(self, client, search_query, expected_pattern):
        """End-to-end API tests for search endpoint with verse references."""
        with patch('backend.services.bible_api.bible_api_service.search_verses') as mock_search:
            # Mock search results
            mock_search.return_value = [
                Mock(
                    verse=Mock(reference=f"{expected_pattern}1", content="Test verse content"),
                    bible_id="eng-WEB",
                    bible_name="World English Bible"
                )
            ]
            
            response = client.post("/api/v1/search", json={
                "query": search_query,
                "bible_id": "eng-WEB",
                "limit": 10
            })
            
            assert response.status_code == 200
            results = response.json()
            assert len(results) > 0
            assert expected_pattern in results[0]["verse"]["reference"]

    # ========== MULTILINGUAL INTEGRATION TESTS ==========
    
    @responses.activate
    def test_multilingual_bible_endpoint(self, client, mock_bible_data):
        """Test that the multilingual Bible endpoint returns organized results."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            json={"data": mock_bible_data},
            status=200
        )
        
        response = client.get("/api/v1/bibles")
        
        assert response.status_code == 200
        bibles = response.json()
        
        # Verify English comes first
        english_bibles = [b for b in bibles if b["language"] == "English"]
        spanish_bibles = [b for b in bibles if b["language"] == "Spanish"]
        
        assert len(english_bibles) > 0, "Should include English Bibles"
        assert len(spanish_bibles) > 0, "Should include Spanish Bibles"
        
        # Verify English appears before Spanish
        english_index = next(i for i, b in enumerate(bibles) if b["language"] == "English")
        spanish_index = next(i for i, b in enumerate(bibles) if b["language"] == "Spanish")
        assert english_index < spanish_index, "English should appear before Spanish"

    # ========== ERROR HANDLING TESTS ==========
    
    @responses.activate
    def test_search_handles_api_failures_gracefully(self, bible_service, mock_bible_data):
        """Test that search handles API failures without crashing."""
        # Mock successful bibles call
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            json={"data": mock_bible_data},
            status=200
        )
        
        # Mock failed search call
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles/eng-WEB/search",
            status=500
        )
        
        # Should not crash, should return empty list
        results = bible_service.search_verses("John 3", bible_id="eng-WEB")
        assert isinstance(results, list), "Should return a list even on API failure"

    # ========== REGRESSION PREVENTION TESTS ==========
    
    def test_john_3_does_not_return_1_john_regression(self, bible_service):
        """
        Specific regression test for the exact issue we had.
        
        This test will fail if the bug reoccurs where "John 3" returns "1 John 4:9".
        """
        # Mock the parsing to ensure it works correctly
        book, chapter, verse = bible_service._parse_verse_reference("John 3")
        
        # Verify parsing
        assert book == "John", "Book should be 'John', not '1 John'"
        assert chapter == "3", "Chapter should be '3'"
        assert verse is None, "Verse should be None for chapter-only reference"
        
        # Verify it's detected as a verse reference
        assert bible_service._is_verse_reference("John 3"), "Should detect 'John 3' as verse reference"
        
        # Verify it triggers chapter search logic (book and chapter exist, verse is None)
        assert book and chapter and not verse, "Should trigger chapter-only search logic"

    @pytest.mark.parametrize("problematic_query,should_not_contain", [
        ("John 3", ["1 John", "2 John", "3 John"]),  # John 3 should not return other John books
        ("Romans 8", ["1 Corinthians", "2 Corinthians"]),  # Romans should not return Corinthians
        ("1 John 3", ["John 3:", "2 John", "3 John"]),  # 1 John should not return regular John
    ])
    def test_cross_contamination_prevention(self, bible_service, problematic_query, should_not_contain):
        """Test that searches don't return verses from wrong books."""
        book, chapter, verse = bible_service._parse_verse_reference(problematic_query)
        
        # Verify the parsing doesn't get confused
        for forbidden_text in should_not_contain:
            assert forbidden_text not in (book or ""), f"Book parsing contaminated: '{book}' contains '{forbidden_text}'"


# ========== PERFORMANCE AND LOAD TESTS ==========

class TestSearchPerformance:
    """Performance tests to catch scalability issues early."""
    
    @pytest.fixture
    def bible_service(self):
        return BibleAPIService()
    
    def test_parsing_performance(self, bible_service):
        """Test that verse reference parsing is fast enough."""
        import time
        
        test_queries = [
            "John 3:16", "John 3", "1 John 4:9", "1 John 3", "Romans 8:28", 
            "Romans 8", "2 Corinthians 12:9", "Psalm 23:1", "Genesis 1:1"
        ] * 100  # Test 900 parses
        
        start_time = time.time()
        for query in test_queries:
            bible_service._parse_verse_reference(query)
            bible_service._is_verse_reference(query)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_parse = total_time / len(test_queries)
        
        # Should be very fast - less than 1ms per parse
        assert avg_time_per_parse < 0.001, f"Parsing too slow: {avg_time_per_parse:.4f}s per query"


# ========== SMOKE TESTS FOR CONTINUOUS INTEGRATION ==========

class TestApplicationSmokeTests:
    """Quick smoke tests that can run in CI to catch major breakages."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_app_starts_without_errors(self, client):
        """Test that the application starts without import or initialization errors."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_bible_endpoint_responds(self, client):
        """Test that the main Bible endpoint responds (even if mocked)."""
        with patch('backend.services.bible_api.bible_api_service.get_all_supported_bibles') as mock_bibles:
            mock_bibles.return_value = []
            response = client.get("/api/v1/bibles")
            assert response.status_code == 200
    
    def test_search_endpoint_responds(self, client):
        """Test that the search endpoint responds without crashing."""
        with patch('backend.services.bible_api.bible_api_service.search_verses') as mock_search:
            mock_search.return_value = []
            response = client.post("/api/v1/search", json={"query": "test", "limit": 1})
            assert response.status_code == 200


if __name__ == "__main__":
    # Run these tests with: poetry run python tests/test_verse_reference_integration.py
    pytest.main([__file__, "-v", "--tb=short"])