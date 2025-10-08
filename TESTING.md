# Faith Dive Testing Guide

This document provides comprehensive information about the Faith Dive testing suite, including how to run tests, write new tests, and understand the testing architecture.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Test Architecture](#test-architecture)
- [Performance Testing](#performance-testing)
- [CI/CD Integration](#cicd-integration)

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Poetry installed
- All dependencies installed: `poetry install --with dev`

### Run Basic Tests

```bash
# Install dependencies
make install

# Run quick tests (recommended for development)
make test-quick

# Run all tests with coverage
make test-all

# Generate coverage report
make coverage
```

## 🏷️ Test Categories

Our testing suite is organized into several categories using pytest markers:

### Unit Tests (`@pytest.mark.unit`)
- Fast, isolated tests
- Test individual functions and classes
- No external dependencies
- Mock all external services

### API Tests (`@pytest.mark.api`)
- Test REST API endpoints
- Validate request/response formats
- Test authentication and authorization
- Verify error handling

### Integration Tests (`@pytest.mark.integration`)
- Test component interactions
- Database operations
- Frontend serving
- Service integrations

### Database Tests (`@pytest.mark.database`)
- SQLAlchemy model tests
- Database operations
- Migration testing
- Data validation

### Services Tests (`@pytest.mark.services`)
- External API integrations
- Business logic
- Service layer functionality
- Error handling and resilience

### Models Tests (`@pytest.mark.models`)
- Pydantic schema validation
- Data model testing
- Serialization/deserialization

### Performance Tests (`@pytest.mark.performance`)
- Response time testing
- Load testing
- Memory usage monitoring
- Scalability testing

### Slow Tests (`@pytest.mark.slow`)
- Long-running tests
- Large dataset testing
- Comprehensive integration tests

### Benchmark Tests (`@pytest.mark.benchmark`)
- Performance benchmarking
- Regression detection
- Performance comparison

## 🏃 Running Tests

### Using Make Commands

```bash
# All tests with coverage
make test

# Quick tests (no slow/performance tests)
make test-quick

# Specific test categories
make test-unit
make test-api
make test-integration
make test-performance

# Parallel execution
make test-parallel

# Benchmarking
make benchmark

# Coverage report
make coverage
```

### Using Test Runner Script

```bash
# Basic usage
python scripts/run_tests.py --help

# Run all tests
python scripts/run_tests.py --all

# Run specific categories
python scripts/run_tests.py --unit
python scripts/run_tests.py --api
python scripts/run_tests.py --integration
python scripts/run_tests.py --performance

# Quick development testing
python scripts/run_tests.py --quick

# Parallel execution
python scripts/run_tests.py --parallel

# Coverage reporting
python scripts/run_tests.py --coverage

# Benchmarking
python scripts/run_tests.py --benchmark
```

### Using Poetry Directly

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=backend --cov-report=html

# Run specific markers
poetry run pytest -m "api"
poetry run pytest -m "unit and not slow"

# Run with specific verbosity
poetry run pytest -v --tb=short

# Run in parallel
poetry run pytest -n auto
```

## 📊 Test Coverage

### Coverage Requirements

- **Minimum Coverage**: 85%
- **Target Coverage**: 90%+
- **Critical Paths**: 95%+

### Coverage Reports

```bash
# Generate HTML report
make coverage
open htmlcov/index.html

# Terminal report
poetry run pytest --cov=backend --cov-report=term-missing

# XML report (for CI)
poetry run pytest --cov=backend --cov-report=xml
```

### Coverage Configuration

Coverage is configured in `pytest.ini`:
- Covers the `backend/` directory
- Excludes test files and migrations
- Fails if coverage falls below 85%
- Generates HTML, XML, and terminal reports

## ✍️ Writing Tests

### Test File Organization

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_health.py             # Health endpoint tests
├── test_bible_endpoints.py    # Bible API tests
├── test_journal_endpoints.py  # Journal API tests
├── test_favorites_endpoints.py # Favorites API tests
├── test_models.py             # Database and schema tests
├── test_services.py           # Service layer tests
├── test_frontend_integration.py # Frontend tests
└── test_performance.py        # Performance and load tests
```

### Writing Unit Tests

```python
import pytest

class TestMyFunction:
    @pytest.mark.unit
    def test_function_success(self):
        """Test successful function execution."""
        result = my_function("input")
        assert result == "expected_output"
    
    @pytest.mark.unit
    def test_function_error_handling(self):
        """Test function error handling."""
        with pytest.raises(ValueError):
            my_function(None)
```

### Writing API Tests

```python
import pytest
from fastapi.testclient import TestClient

class TestMyEndpoint:
    @pytest.mark.api
    def test_get_endpoint(self, client: TestClient):
        """Test GET endpoint."""
        response = client.get("/api/v1/my-endpoint")
        assert response.status_code == 200
        assert "expected_key" in response.json()
    
    @pytest.mark.api
    def test_post_endpoint_validation(self, client: TestClient):
        """Test POST endpoint validation."""
        invalid_data = {"invalid": "data"}
        response = client.post("/api/v1/my-endpoint", json=invalid_data)
        assert response.status_code == 422
```

### Writing Database Tests

```python
import pytest
from backend.models.database import MyModel

class TestMyModel:
    @pytest.mark.database
    @pytest.mark.models
    def test_model_creation(self, test_db):
        """Test model creation."""
        instance = MyModel(field="value")
        test_db.add(instance)
        test_db.commit()
        test_db.refresh(instance)
        
        assert instance.id is not None
        assert instance.field == "value"
```

### Using Fixtures

Common fixtures available in `conftest.py`:

- `test_db`: Test database session
- `client`: FastAPI test client
- `journal_entry_factory`: Factory for journal entries
- `favorite_verse_factory`: Factory for favorite verses
- `mock_bible_api_service`: Mocked Bible API service
- `sample_journal_entry_data`: Sample data for testing

## 🏗️ Test Architecture

### Test Configuration

- **pytest.ini**: Main pytest configuration
- **conftest.py**: Shared fixtures and setup
- Test database uses SQLite in-memory for speed
- Mocking for external services (Bible API)

### Fixtures and Factories

We use Factory Boy for generating test data:

```python
# Using factories
entries = journal_entry_factory.create_batch(10)
favorite = favorite_verse_factory.create()

# Using fixtures
def test_with_sample_data(sample_journal_entry_data):
    assert sample_journal_entry_data["verse_reference"]
```

### Mocking External Services

```python
@pytest.mark.api
def test_with_mocked_bible_api(mock_successful_bible_api):
    """Test uses mocked Bible API responses."""
    # mock_successful_bible_api is automatically configured
    pass
```

## ⚡ Performance Testing

### Performance Test Categories

1. **Response Time Tests**: API endpoint response times
2. **Load Tests**: Concurrent request handling
3. **Scalability Tests**: Performance with large datasets
4. **Memory Tests**: Memory usage monitoring
5. **Benchmark Tests**: Performance regression detection

### Running Performance Tests

```bash
# All performance tests
make test-performance

# Benchmark tests only
make benchmark

# Performance with detailed timing
poetry run pytest -m performance --durations=20
```

### Writing Performance Tests

```python
@pytest.mark.performance
@pytest.mark.slow
def test_endpoint_performance(self, client: TestClient):
    """Test endpoint response time."""
    times = []
    for _ in range(10):
        start_time = time.time()
        response = client.get("/api/v1/endpoint")
        end_time = time.time()
        
        assert response.status_code == 200
        times.append(end_time - start_time)
    
    avg_time = statistics.mean(times)
    assert avg_time < 0.1  # 100ms average
```

## 🤖 CI/CD Integration

### Continuous Integration

```bash
# Basic CI test suite (fast)
make ci-test

# Full CI suite (includes linting)
make ci-full
```

### GitHub Actions / GitLab CI

Example workflow steps:

```yaml
- name: Install dependencies
  run: make install

- name: Run quick tests
  run: make test-quick

- name: Generate coverage
  run: make coverage

- name: Upload coverage
  run: upload-coverage-report
```

### Test Environment Variables

Set these for CI environments:

- `BIBLE_API_KEY`: Test API key
- `DATABASE_URL`: Test database URL
- `DEBUG`: Set to `true` for detailed logging

## 📈 Coverage and Quality Gates

### Quality Requirements

- **Test Coverage**: ≥85%
- **Performance**: API endpoints <500ms
- **Code Quality**: Linting passes
- **Security**: No known vulnerabilities

### Coverage Exclusions

The following are excluded from coverage:

- Test files (`tests/`)
- Database migrations
- Configuration files
- Build scripts

## 🔍 Debugging Tests

### Running Specific Tests

```bash
# Single test file
poetry run pytest tests/test_api.py

# Single test class
poetry run pytest tests/test_api.py::TestMyEndpoint

# Single test method
poetry run pytest tests/test_api.py::TestMyEndpoint::test_specific_case

# Tests matching pattern
poetry run pytest -k "test_journal"
```

### Debugging Options

```bash
# Show detailed output
poetry run pytest -v -s

# Show local variables on failure
poetry run pytest --tb=long

# Drop into debugger on failure
poetry run pytest --pdb

# Show coverage for specific files
poetry run pytest --cov=backend.api --cov-report=term-missing
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Errors**: Ensure test database is clean
2. **Import Errors**: Check Python path and dependencies
3. **Slow Tests**: Use `--durations=10` to identify slow tests
4. **Memory Issues**: Monitor with `psutil` in performance tests

### Getting Help

- Check test logs for detailed error messages
- Run tests with `-v` for verbose output
- Use `--pdb` to debug failing tests
- Check the project's issue tracker for known problems

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)