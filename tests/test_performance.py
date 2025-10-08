import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
import statistics
from unittest.mock import patch


class TestAPIPerformance:
    """Test API endpoint performance."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_health_endpoint_performance(self, client: TestClient):
        """Test health endpoint response time."""
        times = []
        
        for _ in range(10):
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # Health endpoint should be very fast
        assert avg_time < 0.1  # 100ms average
        assert max_time < 0.5  # 500ms max
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_journal_crud_performance(self, client: TestClient, sample_journal_entry_data):
        """Test journal CRUD operations performance."""
        times = {
            'create': [],
            'read': [],
            'update': [],
            'delete': []
        }
        
        created_ids = []
        
        # Test CREATE performance
        for i in range(5):
            entry_data = sample_journal_entry_data.copy()
            entry_data['title'] = f"Performance Test {i}"
            
            start_time = time.time()
            response = client.post("/api/v1/journal", json=entry_data)
            end_time = time.time()
            
            assert response.status_code == 200
            times['create'].append(end_time - start_time)
            created_ids.append(response.json()["id"])
        
        # Test READ performance
        for entry_id in created_ids:
            start_time = time.time()
            response = client.get(f"/api/v1/journal/{entry_id}")
            end_time = time.time()
            
            assert response.status_code == 200
            times['read'].append(end_time - start_time)
        
        # Test UPDATE performance
        for entry_id in created_ids:
            update_data = {"title": f"Updated Entry {entry_id}"}
            
            start_time = time.time()
            response = client.put(f"/api/v1/journal/{entry_id}", json=update_data)
            end_time = time.time()
            
            assert response.status_code == 200
            times['update'].append(end_time - start_time)
        
        # Test DELETE performance
        for entry_id in created_ids:
            start_time = time.time()
            response = client.delete(f"/api/v1/journal/{entry_id}")
            end_time = time.time()
            
            assert response.status_code == 200
            times['delete'].append(end_time - start_time)
        
        # Verify performance requirements
        for operation, time_list in times.items():
            avg_time = statistics.mean(time_list)
            max_time = max(time_list)
            
            # All CRUD operations should be reasonably fast
            assert avg_time < 0.5, f"{operation} average time too slow: {avg_time:.3f}s"
            assert max_time < 1.0, f"{operation} max time too slow: {max_time:.3f}s"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_journal_list_performance_with_pagination(self, client: TestClient, journal_entry_factory):
        """Test journal list performance with different page sizes."""
        # Create test data
        journal_entry_factory.create_batch(50)
        
        pagination_tests = [
            (0, 10),   # First page, small
            (10, 10),  # Second page
            (0, 25),   # Larger page size
            (25, 25),  # Second large page
            (0, 50),   # All items
        ]
        
        for skip, limit in pagination_tests:
            start_time = time.time()
            response = client.get(f"/api/v1/journal?skip={skip}&limit={limit}")
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            
            # Pagination should not significantly impact performance
            assert response_time < 0.5, f"Pagination query too slow: {response_time:.3f}s for skip={skip}, limit={limit}"
            
            data = response.json()
            expected_count = min(limit, max(0, 50 - skip))
            assert len(data) == expected_count
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_api_search_performance(self, client: TestClient, mock_successful_bible_api):
        """Test Bible search API performance."""
        search_queries = [
            {"query": "love", "limit": 10},
            {"query": "peace", "limit": 5},
            {"query": "hope", "limit": 20},
            {"query": "John 3:16", "limit": 1},
        ]
        
        times = []
        
        for search_data in search_queries:
            start_time = time.time()
            response = client.post("/api/v1/search", json=search_data)
            end_time = time.time()
            
            assert response.status_code == 200
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # Search should be reasonably fast even with external API
        assert avg_time < 1.0  # 1 second average (includes mock API time)
        assert max_time < 2.0  # 2 seconds max


class TestLoadTesting:
    """Test application behavior under load."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_health_checks(self, client: TestClient):
        """Test concurrent requests to health endpoint."""
        def make_request():
            response = client.get("/health")
            return response.status_code, time.time()
        
        # Make 20 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]
            total_time = time.time() - start_time
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        assert all(code == 200 for code in status_codes)
        
        # Total time should be reasonable for concurrent requests
        assert total_time < 5.0  # 5 seconds for 20 concurrent requests
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_journal_operations(self, client: TestClient):
        """Test concurrent journal creation and reading."""
        def create_journal_entry(index):
            entry_data = {
                "verse_reference": f"Test {index}:1",
                "verse_text": f"Test verse {index}",
                "bible_version": "TEST",
                "bible_id": "test",
                "content": f"Test content {index}"
            }
            response = client.post("/api/v1/journal", json=entry_data)
            return response.status_code, response.json().get("id") if response.status_code == 200 else None
        
        def read_journal_entries():
            response = client.get("/api/v1/journal")
            return response.status_code, len(response.json()) if response.status_code == 200 else 0
        
        # Test concurrent creates
        with ThreadPoolExecutor(max_workers=5) as executor:
            create_futures = [executor.submit(create_journal_entry, i) for i in range(10)]
            create_results = [future.result() for future in as_completed(create_futures)]
        
        # Test concurrent reads
        with ThreadPoolExecutor(max_workers=5) as executor:
            read_futures = [executor.submit(read_journal_entries) for _ in range(10)]
            read_results = [future.result() for future in as_completed(read_futures)]
        
        # Verify results
        successful_creates = sum(1 for status, _ in create_results if status == 200)
        successful_reads = sum(1 for status, _ in read_results if status == 200)
        
        assert successful_creates >= 8  # Most creates should succeed
        assert successful_reads == 10   # All reads should succeed
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_memory_usage_under_load(self, client: TestClient, journal_entry_factory):
        """Test memory usage during intensive operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create many entries
        journal_entry_factory.create_batch(100)
        
        # Make many API calls
        for _ in range(50):
            response = client.get("/api/v1/journal?limit=20")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory usage should not increase dramatically
        assert memory_increase < 100  # Less than 100MB increase
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_database_connection_pool_under_load(self, client: TestClient):
        """Test database connection handling under load."""
        def make_database_request():
            # This request hits the database
            response = client.get("/api/v1/journal")
            return response.status_code == 200
        
        # Make many concurrent database requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_database_request) for _ in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        # All requests should succeed (no connection pool exhaustion)
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.95  # At least 95% success rate


class TestPerformanceOptimization:
    """Test performance optimization features."""
    
    @pytest.mark.performance
    def test_database_query_optimization(self, client: TestClient, journal_entry_factory):
        """Test that database queries are optimized."""
        # Create a larger dataset
        entries = journal_entry_factory.create_batch(100)
        
        # Test that queries with different filters perform well
        test_cases = [
            "/api/v1/journal?skip=0&limit=10",
            "/api/v1/journal?skip=50&limit=10", 
            "/api/v1/journal?skip=90&limit=10",
        ]
        
        times = []
        for endpoint in test_cases:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            assert response.status_code == 200
            times.append(end_time - start_time)
        
        # Query time should be consistent regardless of offset
        time_variance = statistics.stdev(times) if len(times) > 1 else 0
        assert time_variance < 0.1  # Low variance indicates good indexing
    
    @pytest.mark.performance
    def test_response_size_optimization(self, client: TestClient, journal_entry_factory):
        """Test that API responses are appropriately sized."""
        # Create entries with varying content sizes
        journal_entry_factory.create_batch(20)
        
        response = client.get("/api/v1/journal?limit=10")
        assert response.status_code == 200
        
        response_size = len(response.content)
        
        # Response should be reasonable size (not too large)
        assert response_size < 100 * 1024  # Less than 100KB for 10 entries
        assert response_size > 1000  # But not empty
    
    @pytest.mark.performance
    @pytest.mark.parametrize("batch_size", [1, 5, 10, 25, 50])
    def test_bulk_operation_scaling(self, client: TestClient, journal_entry_factory, batch_size):
        """Test how operations scale with different batch sizes."""
        start_time = time.time()
        entries = journal_entry_factory.create_batch(batch_size)
        creation_time = time.time() - start_time
        
        start_time = time.time()
        response = client.get(f"/api/v1/journal?limit={batch_size}")
        read_time = time.time() - start_time
        
        assert response.status_code == 200
        assert len(response.json()) == batch_size
        
        # Operations should scale reasonably linearly
        creation_per_item = creation_time / batch_size
        read_per_item = read_time / batch_size
        
        assert creation_per_item < 0.1  # Less than 100ms per item creation
        assert read_per_item < 0.01   # Less than 10ms per item read


class TestPerformanceBenchmarks:
    """Performance benchmarks and regression tests."""
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_api_response_time_benchmarks(self, client: TestClient, benchmark):
        """Benchmark API response times using pytest-benchmark."""
        def make_health_request():
            response = client.get("/health")
            assert response.status_code == 200
            return response
        
        # Benchmark the health endpoint
        result = benchmark(make_health_request)
        assert result.status_code == 200
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_journal_creation_benchmark(self, client: TestClient, benchmark, sample_journal_entry_data):
        """Benchmark journal entry creation."""
        def create_journal_entry():
            response = client.post("/api/v1/journal", json=sample_journal_entry_data)
            assert response.status_code == 200
            return response.json()["id"]
        
        # Benchmark journal creation
        entry_id = benchmark(create_journal_entry)
        assert entry_id is not None
        
        # Clean up
        client.delete(f"/api/v1/journal/{entry_id}")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_journal_list_benchmark(self, client: TestClient, benchmark, journal_entry_factory):
        """Benchmark journal entry listing."""
        # Setup: Create test data
        journal_entry_factory.create_batch(50)
        
        def get_journal_list():
            response = client.get("/api/v1/journal?limit=20")
            assert response.status_code == 200
            return response.json()
        
        # Benchmark the list operation
        entries = benchmark(get_journal_list)
        assert len(entries) == 20
    
    @pytest.mark.performance
    def test_performance_regression_detection(self, client: TestClient):
        """Test for performance regressions by checking response times."""
        # This test would ideally compare against historical baselines
        # For now, we just ensure operations complete within reasonable time
        
        operations = [
            ("GET", "/health", None),
            ("GET", "/api/v1/journal", None),
            ("GET", "/api/v1/favorites", None),
        ]
        
        performance_data = {}
        
        for method, endpoint, data in operations:
            times = []
            for _ in range(5):
                start_time = time.time()
                if method == "GET":
                    response = client.get(endpoint)
                elif method == "POST":
                    response = client.post(endpoint, json=data)
                end_time = time.time()
                
                assert response.status_code in [200, 500]  # Either success or expected API error
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            performance_data[f"{method} {endpoint}"] = avg_time
        
        # Define performance thresholds
        thresholds = {
            "GET /health": 0.1,
            "GET /api/v1/journal": 0.5,
            "GET /api/v1/favorites": 0.5,
        }
        
        # Check for regressions
        for operation, avg_time in performance_data.items():
            if operation in thresholds:
                threshold = thresholds[operation]
                assert avg_time < threshold, f"{operation} too slow: {avg_time:.3f}s > {threshold}s"


class TestScalabilityLimits:
    """Test application behavior at scale limits."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_dataset_handling(self, client: TestClient, journal_entry_factory):
        """Test handling of large datasets."""
        # Create a large number of entries
        large_batch_size = 500
        journal_entry_factory.create_batch(large_batch_size)
        
        # Test pagination with large dataset
        start_time = time.time()
        response = client.get("/api/v1/journal?skip=0&limit=100")
        end_time = time.time()
        
        assert response.status_code == 200
        assert len(response.json()) == 100
        
        # Should still be responsive even with large dataset
        response_time = end_time - start_time
        assert response_time < 2.0  # 2 second max for large dataset query
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_high_concurrency_limits(self, client: TestClient):
        """Test behavior under high concurrency."""
        def make_request(request_id):
            try:
                response = client.get(f"/health")
                return response.status_code == 200, request_id
            except Exception as e:
                return False, request_id
        
        # Test with high concurrency
        num_requests = 100
        max_workers = 50
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [future.result() for future in as_completed(futures, timeout=30)]
        
        successful_requests = sum(1 for success, _ in results if success)
        success_rate = successful_requests / num_requests
        
        # Should handle high concurrency reasonably well
        assert success_rate >= 0.9  # At least 90% success rate under high load