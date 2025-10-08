import os
import sys
import pytest
import tempfile
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import factory
from faker import Faker

# Ensure project root is on sys.path so 'backend' can be imported in tests
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.main import app
from backend.database.connection import get_db, Base
from backend.models.database import JournalEntry, FavoriteVerse
from backend.core.config import settings

fake = Faker()

# Test Database Setup
@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function."""
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db) -> Generator[TestClient, None, None]:
    """Create a test client with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Mock authentication headers for future auth implementation."""
    return {"Authorization": "Bearer mock-token"}

# Data Factories
class JournalEntryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = JournalEntry
        sqlalchemy_session_persistence = "commit"

    verse_reference = factory.LazyAttribute(lambda _: f"{fake.random_element(['John', 'Matthew', 'Psalms', 'Romans'])} {fake.random_int(1, 30)}:{fake.random_int(1, 50)}")
    verse_text = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    bible_version = factory.LazyAttribute(lambda _: fake.random_element(["NIV", "ESV", "NLT", "NASB"]))
    bible_id = factory.LazyAttribute(lambda _: fake.uuid4())
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    content = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=500))
    tags = factory.LazyAttribute(lambda _: [fake.word() for _ in range(fake.random_int(1, 5))])

class FavoriteVerseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FavoriteVerse
        sqlalchemy_session_persistence = "commit"

    verse_reference = factory.LazyAttribute(lambda _: f"{fake.random_element(['John', 'Matthew', 'Psalms', 'Romans'])} {fake.random_int(1, 30)}:{fake.random_int(1, 50)}")
    verse_text = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    bible_version = factory.LazyAttribute(lambda _: fake.random_element(["NIV", "ESV", "NLT", "NASB"]))
    bible_id = factory.LazyAttribute(lambda _: fake.uuid4())
    notes = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=300) if fake.boolean() else None)

@pytest.fixture
def journal_entry_factory(test_db):
    """Factory for creating journal entries."""
    JournalEntryFactory._meta.sqlalchemy_session = test_db
    return JournalEntryFactory

@pytest.fixture
def favorite_verse_factory(test_db):
    """Factory for creating favorite verses."""
    FavoriteVerseFactory._meta.sqlalchemy_session = test_db
    return FavoriteVerseFactory

# Mock Data
@pytest.fixture
def mock_bible_versions():
    """Mock Bible versions data."""
    return [
        {
            "id": "eng-NIV",
            "name": "New International Version",
            "abbreviation": "NIV",
            "language": "eng",
            "countries": ["US", "GB"]
        },
        {
            "id": "eng-ESV",
            "name": "English Standard Version",
            "abbreviation": "ESV",
            "language": "eng",
            "countries": ["US"]
        },
        {
            "id": "eng-NLT",
            "name": "New Living Translation",
            "abbreviation": "NLT",
            "language": "eng",
            "countries": ["US"]
        }
    ]

@pytest.fixture
def mock_search_results():
    """Mock Bible search results."""
    return [
        {
            "verse": {
                "reference": "John 3:16",
                "content": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
                "id": "JHN.3.16"
            },
            "bible_name": "New International Version",
            "bible_id": "eng-NIV"
        },
        {
            "verse": {
                "reference": "Romans 8:28",
                "content": "And we know that in all things God works for the good of those who love him, who have been called according to his purpose.",
                "id": "ROM.8.28"
            },
            "bible_name": "New International Version",
            "bible_id": "eng-NIV"
        }
    ]

@pytest.fixture
def mock_verse_data():
    """Mock individual verse data."""
    return {
        "reference": "John 3:16",
        "content": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
        "id": "JHN.3.16",
        "bible_name": "New International Version",
        "bible_id": "eng-NIV"
    }

# API Mocking
@pytest.fixture
def mock_bible_api_service():
    """Mock the Bible API service."""
    with patch('backend.services.bible_api.bible_api_service') as mock_service:
        yield mock_service

@pytest.fixture
def mock_successful_bible_api(mock_bible_api_service, mock_bible_versions, mock_search_results):
    """Configure Bible API service with successful responses."""
    mock_bible_api_service.get_english_bibles.return_value = mock_bible_versions
    mock_bible_api_service.search_verses.return_value = mock_search_results
    mock_bible_api_service.get_verse.return_value = mock_search_results[0]
    return mock_bible_api_service

# Test Data Samples
@pytest.fixture
def sample_journal_entry_data():
    """Sample journal entry data for testing."""
    return {
        "verse_reference": "John 3:16",
        "verse_text": "For God so loved the world...",
        "bible_version": "NIV",
        "bible_id": "eng-NIV",
        "title": "God's Love",
        "content": "This verse reminds me of God's incredible love for humanity.",
        "tags": ["love", "salvation", "eternal life"]
    }

@pytest.fixture
def sample_favorite_verse_data():
    """Sample favorite verse data for testing."""
    return {
        "verse_reference": "Philippians 4:13",
        "verse_text": "I can do all this through him who gives me strength.",
        "bible_version": "NIV",
        "bible_id": "eng-NIV",
        "notes": "My go-to verse for encouragement"
    }

# Environment and Configuration
@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("BIBLE_API_KEY=test_key\n")
        f.write("DATABASE_URL=sqlite:///test.db\n")
        f.write("DEBUG=True\n")
        temp_file = f.name
    
    yield temp_file
    
    os.unlink(temp_file)

@pytest.fixture
def mock_settings():
    """Mock application settings."""
    with patch.object(settings, 'bible_api_key', 'test_key'):
        with patch.object(settings, 'debug', True):
            yield settings

# Performance Testing Fixtures
@pytest.fixture
def large_dataset(test_db, journal_entry_factory):
    """Create a large dataset for performance testing."""
    entries = journal_entry_factory.create_batch(100)
    test_db.commit()
    return entries

# Cleanup
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up any test files created during testing."""
    yield
    # Clean up test database files
    test_files = ['test.db', 'test.db-journal']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
