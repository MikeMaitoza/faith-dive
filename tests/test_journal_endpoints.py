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
