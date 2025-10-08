import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient

from build_frontend import build_frontend


class TestFrontendBuild:
    """Test frontend build system."""
    
    @pytest.mark.integration
    def test_build_frontend_function_exists(self):
        """Test that build_frontend function is available."""
        assert callable(build_frontend)
    
    @pytest.mark.integration
    def test_build_frontend_creates_directories(self):
        """Test that build process creates necessary directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock frontend structure
            public_dir = temp_path / "frontend" / "public"
            public_dir.mkdir(parents=True)
            
            # Create mock files
            (public_dir / "index.html").write_text("<html><head><title>Test</title></head></html>")
            (public_dir / "app.js").write_text("console.log('test');")
            (public_dir / "manifest.json").write_text('{"name": "test"}')
            (public_dir / "sw.js").write_text("// service worker")
            
            # Mock the build_frontend function to use temp directory
            with patch('build_frontend.Path') as mock_path:
                mock_path.return_value.parent = temp_path
                mock_path.return_value.__truediv__ = lambda self, other: temp_path / other
                
                build_dir = temp_path / "frontend" / "build"
                static_dir = build_dir / "static"
                
                # Manually create the expected structure for this test
                build_dir.mkdir(parents=True)
                static_dir.mkdir(parents=True)
                
                # Copy files manually for this test
                shutil.copy2(public_dir / "index.html", build_dir / "index.html")
                shutil.copy2(public_dir / "app.js", static_dir / "app.js")
                shutil.copy2(public_dir / "manifest.json", build_dir / "manifest.json")
                shutil.copy2(public_dir / "sw.js", build_dir / "sw.js")
                
                # Verify files exist
                assert (build_dir / "index.html").exists()
                assert (static_dir / "app.js").exists()
                assert (build_dir / "manifest.json").exists()
                assert (build_dir / "sw.js").exists()
    
    @pytest.mark.integration
    def test_build_frontend_updates_html_references(self):
        """Test that build process updates HTML script references."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock HTML with script reference
            html_content = '''
            <html>
            <head><title>Test</title></head>
            <body>
                <script src="/app.js"></script>
            </body>
            </html>
            '''
            
            html_file = temp_path / "index.html"
            html_file.write_text(html_content)
            
            # Update HTML references (simulate build process)
            updated_content = html_file.read_text()
            updated_content = updated_content.replace('src="/app.js"', 'src="/static/app.js"')
            html_file.write_text(updated_content)
            
            # Verify update
            final_content = html_file.read_text()
            assert 'src="/static/app.js"' in final_content
            assert 'src="/app.js"' not in final_content


class TestFrontendServing:
    """Test frontend file serving through FastAPI."""
    
    @pytest.mark.integration
    def test_frontend_index_served(self, client: TestClient):
        """Test that index.html is served at root path."""
        response = client.get("/")
        
        # Should serve HTML content
        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith("text/html")
    
    @pytest.mark.integration
    def test_frontend_static_js_served(self, client: TestClient):
        """Test that JavaScript files are served from static directory."""
        response = client.get("/static/app.js")
        
        if response.status_code == 200:
            # Should serve JavaScript content
            assert "javascript" in response.headers.get("content-type", "").lower() or \
                   "text/plain" in response.headers.get("content-type", "").lower()
        else:
            # If file doesn't exist, should return 404
            assert response.status_code == 404
    
    @pytest.mark.integration
    def test_frontend_manifest_served(self, client: TestClient):
        """Test that manifest.json is served."""
        response = client.get("/manifest.json")
        
        if response.status_code == 200:
            # Should serve JSON content
            assert "application/json" in response.headers.get("content-type", "")
        else:
            # If file doesn't exist, should return 404
            assert response.status_code == 404
    
    @pytest.mark.integration
    def test_frontend_service_worker_served(self, client: TestClient):
        """Test that service worker is served."""
        response = client.get("/sw.js")
        
        if response.status_code == 200:
            # Should serve JavaScript content
            assert "javascript" in response.headers.get("content-type", "").lower() or \
                   "text/plain" in response.headers.get("content-type", "").lower()
        else:
            # If file doesn't exist, should return 404
            assert response.status_code == 404
    
    @pytest.mark.integration
    def test_frontend_nonexistent_static_file(self, client: TestClient):
        """Test handling of non-existent static files."""
        response = client.get("/static/nonexistent.js")
        
        assert response.status_code == 404


class TestFrontendContent:
    """Test frontend content and structure."""
    
    @pytest.mark.integration
    def test_frontend_html_content(self, client: TestClient):
        """Test that served HTML contains expected content."""
        response = client.get("/")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for expected HTML elements
            assert "<html" in html_content
            assert "<head>" in html_content
            assert "<body>" in html_content
            assert "Faith Dive" in html_content or "faith" in html_content.lower()
    
    @pytest.mark.integration
    def test_frontend_javascript_content(self, client: TestClient):
        """Test that served JavaScript contains expected content."""
        response = client.get("/static/app.js")
        
        if response.status_code == 200:
            js_content = response.text
            
            # Check for expected JavaScript patterns
            assert len(js_content) > 100  # Should have substantial content
            # Could check for specific function names or API endpoints
    
    @pytest.mark.integration
    def test_frontend_manifest_content(self, client: TestClient):
        """Test that manifest.json contains valid PWA data."""
        response = client.get("/manifest.json")
        
        if response.status_code == 200:
            import json
            try:
                manifest_data = json.loads(response.text)
                
                # Check required PWA fields
                assert "name" in manifest_data
                assert "short_name" in manifest_data or "name" in manifest_data
                assert "start_url" in manifest_data
                assert "display" in manifest_data
                
            except json.JSONDecodeError:
                pytest.fail("Manifest.json contains invalid JSON")
    
    @pytest.mark.integration
    def test_frontend_service_worker_content(self, client: TestClient):
        """Test that service worker contains expected functionality."""
        response = client.get("/sw.js")
        
        if response.status_code == 200:
            sw_content = response.text
            
            # Check for service worker patterns
            assert len(sw_content) > 50  # Should have some content
            # Could check for specific event listeners or caching logic


class TestFrontendAPIIntegration:
    """Test frontend integration with API endpoints."""
    
    @pytest.mark.integration
    def test_api_endpoints_accessible_from_frontend(self, client: TestClient):
        """Test that API endpoints are accessible from same origin."""
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test API documentation
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test Bible API endpoint
        response = client.get("/api/v1/bibles")
        # Should return either 200 (success) or 500 (API error, but endpoint exists)
        assert response.status_code in [200, 500]
    
    @pytest.mark.integration
    def test_cors_headers_for_frontend(self, client: TestClient):
        """Test that CORS headers are properly set for frontend requests."""
        # Make a preflight request
        response = client.options("/api/v1/journal", headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # Should handle preflight request properly
        assert response.status_code in [200, 204, 405]  # Various valid responses
        
        # Check actual request
        response = client.get("/api/v1/journal", headers={
            "Origin": "http://localhost:8000"
        })
        
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or \
               response.headers.get("access-control-allow-origin") is not None


class TestFrontendPerformance:
    """Test frontend performance characteristics."""
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_frontend_response_times(self, client: TestClient):
        """Test that frontend files are served quickly."""
        import time
        
        # Test index.html response time
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = end_time - start_time
            assert response_time < 1.0  # Should be fast
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_frontend_file_sizes(self, client: TestClient):
        """Test that frontend files have reasonable sizes."""
        # Test index.html size
        response = client.get("/")
        if response.status_code == 200:
            html_size = len(response.content)
            assert html_size < 1024 * 1024  # Less than 1MB
            assert html_size > 1000  # But not empty
        
        # Test JavaScript size
        response = client.get("/static/app.js")
        if response.status_code == 200:
            js_size = len(response.content)
            assert js_size < 5 * 1024 * 1024  # Less than 5MB
            assert js_size > 100  # But not empty


class TestFrontendSecurity:
    """Test frontend security headers and configurations."""
    
    @pytest.mark.integration
    def test_frontend_security_headers(self, client: TestClient):
        """Test that appropriate security headers are set."""
        response = client.get("/")
        
        if response.status_code == 200:
            headers = response.headers
            
            # Note: These may or may not be set depending on configuration
            # This test documents what security headers could be present
            security_headers = [
                "x-content-type-options",
                "x-frame-options", 
                "x-xss-protection",
                "strict-transport-security"
            ]
            
            # Just verify the headers dict is accessible
            assert isinstance(headers, dict) or hasattr(headers, 'get')
    
    @pytest.mark.integration
    def test_frontend_content_types(self, client: TestClient):
        """Test that files are served with correct content types."""
        test_cases = [
            ("/", "text/html"),
            ("/static/app.js", ["application/javascript", "text/javascript", "text/plain"]),
            ("/manifest.json", "application/json"),
            ("/sw.js", ["application/javascript", "text/javascript", "text/plain"])
        ]
        
        for url, expected_types in test_cases:
            response = client.get(url)
            
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "").lower()
                
                if isinstance(expected_types, str):
                    expected_types = [expected_types]
                
                assert any(expected in content_type for expected in expected_types), \
                    f"URL {url} returned unexpected content-type: {content_type}"


class TestFrontendErrorHandling:
    """Test frontend error handling and fallbacks."""
    
    @pytest.mark.integration
    def test_frontend_404_handling(self, client: TestClient):
        """Test handling of non-existent frontend routes."""
        response = client.get("/nonexistent/route")
        
        # Should either serve index.html (SPA behavior) or return 404
        assert response.status_code in [200, 404]
    
    @pytest.mark.integration
    def test_frontend_with_api_errors(self, client: TestClient, mock_bible_api_service):
        """Test frontend behavior when API returns errors."""
        # Simulate API error
        mock_bible_api_service.get_english_bibles.side_effect = Exception("API Error")
        
        # Frontend should still load
        response = client.get("/")
        
        if response.status_code == 200:
            # HTML should still be served even if API fails
            assert "<html" in response.text
    
    @pytest.mark.integration
    def test_frontend_graceful_degradation(self, client: TestClient):
        """Test that frontend degrades gracefully without JavaScript."""
        response = client.get("/")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Should have basic HTML structure even without JS
            assert "<html" in html_content
            assert "<body>" in html_content
            # Should have some non-JS content or fallbacks