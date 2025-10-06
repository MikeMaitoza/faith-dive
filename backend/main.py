from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
from contextlib import asynccontextmanager

from backend.core.config import settings
from backend.database.connection import get_db, create_tables
from backend.models import database, schemas
from backend.services.bible_api import bible_api_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables at startup
    create_tables()
    yield

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A Progressive Web App for Bible verse search and journaling",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bible API Routes
@app.get(f"{settings.api_prefix}/bibles", response_model=List[schemas.BibleVersion])
async def get_english_bibles():
    """Get all available English Bible versions"""
    bibles = bible_api_service.get_english_bibles()
    return bibles

@app.post(f"{settings.api_prefix}/search", response_model=List[schemas.SearchResult])
async def search_verses(search_request: schemas.SearchRequest):
    """Search for Bible verses"""
    results = bible_api_service.search_verses(
        query=search_request.query,
        bible_id=search_request.bible_id,
        limit=search_request.limit or 10
    )
    return results

@app.get(f"{settings.api_prefix}/verses/{{verse_id}}")
async def get_verse(verse_id: str, bible_id: str):
    """Get a specific verse by ID"""
    verse = bible_api_service.get_verse(verse_id, bible_id)
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")
    return verse

# Journal Entry Routes
@app.post(f"{settings.api_prefix}/journal", response_model=schemas.JournalEntryResponse)
async def create_journal_entry(
    entry: schemas.JournalEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new journal entry"""
    db_entry = database.JournalEntry(
        verse_reference=entry.verse_reference,
        verse_text=entry.verse_text,
        bible_version=entry.bible_version,
        bible_id=entry.bible_id,
        title=entry.title,
        content=entry.content,
        tags=entry.tags
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.get(f"{settings.api_prefix}/journal", response_model=List[schemas.JournalEntryResponse])
async def get_journal_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all journal entries"""
    entries = db.query(database.JournalEntry).offset(skip).limit(limit).all()
    return entries

@app.get(f"{settings.api_prefix}/journal/{{entry_id}}", response_model=schemas.JournalEntryResponse)
async def get_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific journal entry"""
    entry = db.query(database.JournalEntry).filter(database.JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry

@app.put(f"{settings.api_prefix}/journal/{{entry_id}}", response_model=schemas.JournalEntryResponse)
async def update_journal_entry(
    entry_id: int,
    entry_update: schemas.JournalEntryUpdate,
    db: Session = Depends(get_db)
):
    """Update a journal entry"""
    db_entry = db.query(database.JournalEntry).filter(database.JournalEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    # Update fields if provided
    if entry_update.title is not None:
        db_entry.title = entry_update.title
    if entry_update.content is not None:
        db_entry.content = entry_update.content
    if entry_update.tags is not None:
        db_entry.tags = entry_update.tags
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.delete(f"{settings.api_prefix}/journal/{{entry_id}}")
async def delete_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a journal entry"""
    db_entry = db.query(database.JournalEntry).filter(database.JournalEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    db.delete(db_entry)
    db.commit()
    return {"message": "Journal entry deleted successfully"}

# Favorite Verses Routes
@app.post(f"{settings.api_prefix}/favorites", response_model=schemas.FavoriteVerseResponse)
async def create_favorite_verse(
    favorite: schemas.FavoriteVerseCreate,
    db: Session = Depends(get_db)
):
    """Add a verse to favorites"""
    db_favorite = database.FavoriteVerse(
        verse_reference=favorite.verse_reference,
        verse_text=favorite.verse_text,
        bible_version=favorite.bible_version,
        bible_id=favorite.bible_id,
        notes=favorite.notes
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

@app.get(f"{settings.api_prefix}/favorites", response_model=List[schemas.FavoriteVerseResponse])
async def get_favorite_verses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all favorite verses"""
    favorites = db.query(database.FavoriteVerse).offset(skip).limit(limit).all()
    return favorites

@app.delete(f"{settings.api_prefix}/favorites/{{favorite_id}}")
async def delete_favorite_verse(favorite_id: int, db: Session = Depends(get_db)):
    """Remove a verse from favorites"""
    db_favorite = db.query(database.FavoriteVerse).filter(database.FavoriteVerse.id == favorite_id).first()
    if not db_favorite:
        raise HTTPException(status_code=404, detail="Favorite verse not found")
    
    db.delete(db_favorite)
    db.commit()
    return {"message": "Favorite verse removed successfully"}

# Serve static files for the frontend
frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
if os.path.exists(frontend_build_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_build_path, "static")), name="static")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_build_path, "index.html"))
    
    @app.get("/manifest.json")
    async def serve_manifest():
        return FileResponse(os.path.join(frontend_build_path, "manifest.json"))
    
    @app.get("/sw.js")
    async def serve_service_worker():
        return FileResponse(os.path.join(frontend_build_path, "sw.js"))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)