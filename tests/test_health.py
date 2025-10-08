import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_endpoint_success(self, client: TestClient):
        """Test health endpoint returns success."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_endpoint_response_format(self, client: TestClient):
        """Test health endpoint response format."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        required_fields = ["status", "version"]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.performance
    def test_health_endpoint_performance(self, client: TestClient):
        """Test health endpoint response time."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.1  # Should respond within 100ms
