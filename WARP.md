# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project: Faith Dive — Bible Journaling PWA (FastAPI backend)

Commands you’ll use most

- Prerequisites
  - Python 3.12+
  - Poetry

- Install dependencies
  - poetry install

- Configure environment
  - cp .env.template .env
  - Add your API.Bible key to .env (BIBLE_API_KEY)

- Run the API (development)
  - Preferred (dev script with reload):
    - poetry run python run.py
  - As defined in README:
    - poetry run python backend/main.py
  - Direct with uvicorn (equivalent):
    - poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
  - API docs: http://localhost:8000/docs

- Tests
  - Run all tests:
    - poetry run pytest -q
  - Run a single test (examples):
    - poetry run pytest tests/path/to/test_file.py::TestClass::test_case -q
    - poetry run pytest -k "search" -q

- Formatting (from README)
  - poetry run black backend/
  - Note: if Black is not installed, add it to your dev dependencies before running the command.

High-level architecture and flow

- Application entrypoint: backend/main.py
  - Creates FastAPI app (title/version from settings)
  - CORS configured via allowed_origins
  - Startup hook creates DB tables
  - Routes:
    - Bible: GET /api/v1/bibles, POST /api/v1/search, GET /api/v1/verses/{verse_id}
      - Delegates to services.bible_api for external API interactions
    - Journal: CRUD at /api/v1/journal (create, list, get, update, delete)
      - Uses SQLAlchemy models (JournalEntry) via a DB session dependency
    - Favorites: create/list/delete at /api/v1/favorites
      - Uses SQLAlchemy models (FavoriteVerse)
    - Health: GET /health
  - Frontend static serving: if ../frontend/build exists, mounts /static and serves index.html at /

- Configuration: backend/core/config.py
  - Settings are loaded from environment (.env) using pydantic-settings and python-dotenv
  - Key values: BIBLE_API_KEY, DATABASE_URL (defaults to sqlite:///./faith_dive.db), app metadata, CORS origins, api_prefix=/api/v1, debug

- Database: backend/database/connection.py and backend/models/
  - Engine/session: created from settings.database_url; SQLite uses check_same_thread=False
  - create_tables() called at startup creates all tables from Base metadata
  - Models (backend/models/database.py):
    - JournalEntry: verse_reference, verse_text, bible_version, bible_id, title, content, tags (JSON), timestamps
    - FavoriteVerse: verse_reference, verse_text, bible_version, bible_id, notes, created_at
  - Pydantic schemas (backend/models/schemas.py):
    - BibleVersion, VerseContent, SearchResult (for external API responses)
    - JournalEntryCreate/Update/Response
    - FavoriteVerseCreate/Response

- External Bible API service: backend/services/bible_api.py
  - BibleAPIService wraps API.Bible via requests with api-key header from env
  - Methods:
    - get_english_bibles(): filters /bibles for language.id == "eng"
    - search_verses(query, bible_id?, limit): hits /bibles/{id}/search, maps results to SearchResult, cleans HTML from content
    - get_verse(verse_id, bible_id): returns a VerseContent for a specific verse
    - get_bible_info(bible_id): fetches metadata used to label results

- Development runner: run.py
  - Convenience dev script printing URLs and running uvicorn with reload over backend and frontend dirs

Migrations

- Initialize DB schema to latest:
  - poetry run alembic upgrade head
- Create a new migration after model changes:
  - poetry run alembic revision --autogenerate -m "<message>"
  - poetry run alembic upgrade head
- Roll back the last migration:
  - poetry run alembic downgrade -1

Notes and alignment with README

- README provides the primary quickstart flow (poetry install, copy .env, poetry run python backend/main.py) and lists features/endpoints that match the current FastAPI routes in backend/main.py.
- README describes a future/idealized structure that includes backend/api/; current routes are defined directly in backend/main.py (no backend/api package in this repo snapshot).
- Alembic configuration is now present (alembic.ini, alembic/). Runtime still creates tables at startup; migrations are recommended for schema changes.
