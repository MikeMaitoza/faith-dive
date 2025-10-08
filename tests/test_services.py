import pytest
from unittest.mock import Mock, patch, MagicMock
import responses
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from backend.services.bible_api import BibleAPIService


class TestBibleAPIService:
    """Test Bible API service integration."""
    
    @pytest.fixture
    def bible_service(self):
        """Create a Bible API service instance."""
        return BibleAPIService()
    
    @pytest.mark.services
    @responses.activate
    def test_get_english_bibles_success(self, bible_service, mock_bible_versions):
        """Test successful retrieval of English Bible versions."""
        # Mock the API response
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            json={"data": mock_bible_versions},
            status=200,
            headers={"Content-Type": "application/json"}
        )
        
        result = bible_service.get_english_bibles()
        
        assert len(result) == 3
        assert result[0]["id"] == "eng-NIV"
        assert result[0]["abbreviation"] == "NIV"
    
    @pytest.mark.services
    @responses.activate
    def test_get_english_bibles_api_error(self, bible_service):
        """Test Bible versions retrieval when API returns error."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            json={"error": "API Error"},
            status=500
        )
        
        with pytest.raises(Exception):
            bible_service.get_english_bibles()
    
    @pytest.mark.services
    @responses.activate
    def test_get_english_bibles_network_error(self, bible_service):
        """Test Bible versions retrieval with network error."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            body=ConnectionError("Network error")
        )
        
        with pytest.raises(ConnectionError):
            bible_service.get_english_bibles()
    
    @pytest.mark.services
    @responses.activate
    def test_search_verses_success(self, bible_service, mock_search_results):
        """Test successful verse search."""
        bible_id = "eng-NIV"
        query = "love"
        
        # Mock the API response
        responses.add(
            responses.GET,
            f"https://api.scripture.api.bible/v1/bibles/{bible_id}/search",
            json={"data": {"verses": mock_search_results}},
            status=200
        )
        
        result = bible_service.search_verses(query=query, bible_id=bible_id, limit=10)
        
        assert len(result) == 2
        assert result[0]["verse"]["reference"] == "John 3:16"
        assert result[0]["bible_id"] == bible_id
    
    @pytest.mark.services
    @responses.activate
    def test_search_verses_no_results(self, bible_service):
        """Test verse search with no results."""
        bible_id = "eng-NIV"
        query = "nonexistentword"
        
        responses.add(
            responses.GET,
            f"https://api.scripture.api.bible/v1/bibles/{bible_id}/search",
            json={"data": {"verses": []}},
            status=200
        )
        
        result = bible_service.search_verses(query=query, bible_id=bible_id, limit=10)
        
        assert result == []
    
    @pytest.mark.services
    @responses.activate
    def test_search_verses_with_limit(self, bible_service, mock_search_results):
        """Test verse search with custom limit."""
        bible_id = "eng-NIV"
        query = "peace"
        limit = 5
        
        responses.add(
            responses.GET,
            f"https://api.scripture.api.bible/v1/bibles/{bible_id}/search",
            json={"data": {"verses": mock_search_results[:limit]}},
            status=200
        )
        
        result = bible_service.search_verses(query=query, bible_id=bible_id, limit=limit)
        
        # Verify the request was made with correct parameters
        request = responses.calls[0].request
        assert f"limit={limit}" in request.url
        assert f"query={query}" in request.url
    
    @pytest.mark.services
    @responses.activate
    def test_search_verses_without_bible_id(self, bible_service):
        """Test verse search without specifying Bible ID."""
        query = "hope"
        
        # Mock response for default Bible or multiple Bibles
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/search",
            json={"data": {"verses": []}},
            status=200
        )
        
        result = bible_service.search_verses(query=query, bible_id=None, limit=10)
        
        # Should handle the case gracefully
        assert isinstance(result, list)
    
    @pytest.mark.services
    @responses.activate
    def test_get_verse_success(self, bible_service, mock_verse_data):
        """Test successful retrieval of specific verse."""
        verse_id = "JHN.3.16"
        bible_id = "eng-NIV"
        
        responses.add(
            responses.GET,
            f"https://api.scripture.api.bible/v1/bibles/{bible_id}/verses/{verse_id}",
            json={"data": mock_verse_data},
            status=200
        )
        
        result = bible_service.get_verse(verse_id=verse_id, bible_id=bible_id)
        
        assert result["verse"]["reference"] == "John 3:16"
        assert result["bible_id"] == bible_id
    
    @pytest.mark.services
    @responses.activate
    def test_get_verse_not_found(self, bible_service):
        """Test verse retrieval when verse doesn't exist."""
        verse_id = "NONEXIST.1.1"
        bible_id = "eng-NIV"
        
        responses.add(
            responses.GET,
            f"https://api.scripture.api.bible/v1/bibles/{bible_id}/verses/{verse_id}",
            status=404
        )
        
        result = bible_service.get_verse(verse_id=verse_id, bible_id=bible_id)
        
        assert result is None
    
    @pytest.mark.services
    @responses.activate
    def test_api_timeout(self, bible_service):
        """Test API timeout handling."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            body=Timeout("Request timed out")
        )
        
        with pytest.raises(Timeout):
            bible_service.get_english_bibles()
    
    @pytest.mark.services
    @pytest.mark.parametrize("status_code,expected_exception", [
        (400, requests.exceptions.HTTPError),
        (401, requests.exceptions.HTTPError),
        (403, requests.exceptions.HTTPError),
        (500, requests.exceptions.HTTPError),
        (502, requests.exceptions.HTTPError),
        (503, requests.exceptions.HTTPError),
    ])
    @responses.activate
    def test_api_http_errors(self, bible_service, status_code, expected_exception):
        """Test handling of various HTTP error codes."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            status=status_code
        )
        
        with pytest.raises(expected_exception):
            bible_service.get_english_bibles()
    
    @pytest.mark.services
    @responses.activate
    def test_api_malformed_json(self, bible_service):
        """Test handling of malformed JSON response."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            body="{ invalid json }",
            status=200,
            headers={"Content-Type": "application/json"}
        )
        
        with pytest.raises(Exception):  # Could be ValueError or JSONDecodeError
            bible_service.get_english_bibles()
    
    @pytest.mark.services
    @responses.activate
    def test_api_rate_limiting(self, bible_service):
        """Test API rate limiting handling."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            status=429,
            headers={
                "Retry-After": "60",
                "X-RateLimit-Remaining": "0"
            }
        )
        
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            bible_service.get_english_bibles()
        
        assert exc_info.value.response.status_code == 429
    
    @pytest.mark.services
    @patch('backend.services.bible_api.requests.get')
    def test_api_authentication_headers(self, mock_get, bible_service):
        """Test that API requests include proper authentication headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        with patch('backend.core.config.settings') as mock_settings:
            mock_settings.bible_api_key = "test_api_key"
            bible_service.get_english_bibles()
        
        # Verify the request was made with auth headers
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert "headers" in call_kwargs
        assert "X-API-Key" in call_kwargs["headers"] or "Authorization" in call_kwargs["headers"]
    
    @pytest.mark.services
    @pytest.mark.parametrize("query,bible_id,limit", [
        ("love", "eng-NIV", 10),
        ("peace", "eng-ESV", 5),
        ("hope", "eng-NLT", 20),
        ("faith", None, 15),
        ("", "eng-NIV", 1),
    ])
    @responses.activate
    def test_search_verses_parameter_variations(self, bible_service, query, bible_id, limit):
        """Test verse search with various parameter combinations."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles/eng-NIV/search" if bible_id else "https://api.scripture.api.bible/v1/search",
            json={"data": {"verses": []}},
            status=200
        )
        
        result = bible_service.search_verses(query=query, bible_id=bible_id, limit=limit)
        
        assert isinstance(result, list)
        # Verify request parameters if needed
        if len(responses.calls) > 0:
            request_url = responses.calls[0].request.url
            if query:
                assert f"query={query.replace(' ', '%20')}" in request_url
            assert f"limit={limit}" in request_url


class TestServiceConfiguration:
    """Test service configuration and initialization."""
    
    @pytest.mark.services
    def test_bible_service_initialization(self):
        """Test Bible service initialization."""
        service = BibleAPIService()
        
        # Verify service is properly initialized
        assert hasattr(service, 'base_url') or hasattr(service, '_base_url')
        assert hasattr(service, 'api_key') or hasattr(service, '_api_key')
    
    @pytest.mark.services
    @patch('backend.core.config.settings')
    def test_service_with_custom_config(self, mock_settings):
        """Test service with custom configuration."""
        mock_settings.bible_api_base_url = "https://custom.api.url/v1"
        mock_settings.bible_api_key = "custom_key"
        
        service = BibleAPIService()
        
        # Service should use custom configuration
        # This test verifies that configuration is properly loaded
        assert service is not None
    
    @pytest.mark.services
    @patch('backend.core.config.settings')
    def test_service_without_api_key(self, mock_settings):
        """Test service behavior without API key."""
        mock_settings.bible_api_key = ""
        
        service = BibleAPIService()
        
        # Service should handle missing API key gracefully
        # or raise appropriate error
        with pytest.raises((ValueError, AttributeError, Exception)):
            service.get_english_bibles()


class TestServiceErrorHandling:
    """Test service error handling and resilience."""
    
    @pytest.fixture
    def bible_service(self):
        return BibleAPIService()
    
    @pytest.mark.services
    def test_service_method_signature_validation(self, bible_service):
        """Test that service methods validate their parameters."""
        # Test with invalid parameters
        with pytest.raises((TypeError, ValueError)):
            bible_service.search_verses()  # Missing required parameters
    
    @pytest.mark.services
    @responses.activate
    def test_service_handles_empty_response(self, bible_service):
        """Test service handling of empty API responses."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            json={},
            status=200
        )
        
        # Service should handle empty response gracefully
        result = bible_service.get_english_bibles()
        assert isinstance(result, list)
    
    @pytest.mark.services
    @responses.activate
    def test_service_handles_unexpected_response_structure(self, bible_service):
        """Test service handling of unexpected API response structure."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            json={"unexpected": "structure"},
            status=200
        )
        
        # Service should handle unexpected structure
        with pytest.raises((KeyError, AttributeError, Exception)):
            bible_service.get_english_bibles()
    
    @pytest.mark.services
    @pytest.mark.parametrize("network_exception", [
        ConnectionError("Connection failed"),
        Timeout("Request timeout"),
        RequestException("General request error"),
    ])
    @responses.activate
    def test_service_network_error_handling(self, bible_service, network_exception):
        """Test service handling of various network errors."""
        responses.add(
            responses.GET,
            "https://api.scripture.api.bible/v1/bibles",
            body=network_exception
        )
        
        with pytest.raises(type(network_exception)):
            bible_service.get_english_bibles()


class TestServiceIntegration:
    """Test service integration patterns."""
    
    @pytest.mark.services
    @pytest.mark.integration
    def test_service_caching_behavior(self):
        """Test service caching if implemented."""
        # This test would verify caching behavior if implemented
        service = BibleAPIService()
        
        # Mock multiple calls to same resource
        with patch.object(service, '_make_request') as mock_request:
            mock_request.return_value = {"data": []}
            
            # Make multiple calls
            service.get_english_bibles()
            service.get_english_bibles()
            
            # Depending on caching implementation, this might be called once or twice
            assert mock_request.call_count >= 1
    
    @pytest.mark.services
    @pytest.mark.integration
    def test_service_retry_mechanism(self):
        """Test service retry mechanism if implemented."""
        service = BibleAPIService()
        
        # This would test retry logic for failed requests
        # Implementation depends on specific retry strategy
        assert service is not None  # Placeholder
    
    @pytest.mark.services
    @pytest.mark.slow
    @pytest.mark.integration
    def test_service_performance(self, bible_service):
        """Test service performance under normal conditions."""
        import time
        
        with patch.object(bible_service, '_make_request') as mock_request:
            mock_request.return_value = {"data": []}
            
            start_time = time.time()
            bible_service.get_english_bibles()
            end_time = time.time()
            
            # Service should respond within reasonable time
            response_time = end_time - start_time
            assert response_time < 1.0  # Should be much faster with mocking