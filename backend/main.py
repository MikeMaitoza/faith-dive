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
from backend.services.study_scheduler import study_scheduler
from sqlalchemy import func, and_
from collections import Counter

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
async def get_all_bibles():
    """Get all available Bible versions in supported languages"""
    bibles = bible_api_service.get_all_supported_bibles()
    return bibles

@app.get(f"{settings.api_prefix}/bibles/english", response_model=List[schemas.BibleVersion])
async def get_english_bibles():
    """Get all available English Bible versions (for backward compatibility)"""
    bibles = bible_api_service.get_english_bibles()
    return bibles

@app.get(f"{settings.api_prefix}/bibles/language/{{language_id}}", response_model=List[schemas.BibleVersion])
async def get_bibles_by_language(language_id: str):
    """Get Bible versions for a specific language"""
    bibles = bible_api_service.get_bibles_by_language(language_id)
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

# Weekly Study Routes
@app.post(f"{settings.api_prefix}/studies", response_model=schemas.WeeklyStudyResponse)
async def create_weekly_study(
    study: schemas.WeeklyStudyCreate,
    db: Session = Depends(get_db)
):
    """Create a new weekly Bible study"""
    db_study = database.WeeklyStudy(
        title=study.title,
        description=study.description,
        verse_references=study.verse_references,
        verse_texts=study.verse_texts,
        bible_version=study.bible_version,
        bible_id=study.bible_id,
        study_questions=study.study_questions,
        study_notes=study.study_notes,
        scheduled_date=study.scheduled_date
    )
    
    # If no scheduled date provided, auto-schedule for next Wednesday
    if not study.scheduled_date:
        study_scheduler.schedule_study_for_next_wednesday(db, db_study)
    
    db.add(db_study)
    db.commit()
    db.refresh(db_study)
    
    # Add response count
    response = schemas.WeeklyStudyResponse.model_validate(db_study)
    response.response_count = 0
    return response

@app.get(f"{settings.api_prefix}/studies", response_model=List[schemas.WeeklyStudyResponse])
async def get_weekly_studies(
    published_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all weekly studies"""
    query = db.query(database.WeeklyStudy)
    if published_only:
        query = query.filter(database.WeeklyStudy.published == True)
    
    studies = query.order_by(database.WeeklyStudy.scheduled_date.desc()).offset(skip).limit(limit).all()
    
    # Add response counts
    result = []
    for study in studies:
        study_response = schemas.WeeklyStudyResponse.model_validate(study)
        study_response.response_count = len([r for r in study.responses if not r.is_hidden])
        result.append(study_response)
    
    return result

@app.get(f"{settings.api_prefix}/studies/current", response_model=schemas.WeeklyStudyResponse)
async def get_current_weekly_study(db: Session = Depends(get_db)):
    """Get the current week's published study"""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    
    study = db.query(database.WeeklyStudy).filter(
        and_(
            database.WeeklyStudy.published == True,
            database.WeeklyStudy.scheduled_date <= now
        )
    ).order_by(database.WeeklyStudy.scheduled_date.desc()).first()
    
    if not study:
        raise HTTPException(status_code=404, detail="No current study available")
    
    study_response = schemas.WeeklyStudyResponse.model_validate(study)
    study_response.response_count = len([r for r in study.responses if not r.is_hidden])
    return study_response

@app.get(f"{settings.api_prefix}/studies/{{study_id}}", response_model=schemas.WeeklyStudyResponse)
async def get_weekly_study(study_id: int, db: Session = Depends(get_db)):
    """Get a specific weekly study"""
    study = db.query(database.WeeklyStudy).filter(database.WeeklyStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    
    study_response = schemas.WeeklyStudyResponse.model_validate(study)
    study_response.response_count = len([r for r in study.responses if not r.is_hidden])
    return study_response

@app.put(f"{settings.api_prefix}/studies/{{study_id}}", response_model=schemas.WeeklyStudyResponse)
async def update_weekly_study(
    study_id: int,
    study_update: schemas.WeeklyStudyUpdate,
    db: Session = Depends(get_db)
):
    """Update a weekly study"""
    db_study = db.query(database.WeeklyStudy).filter(database.WeeklyStudy.id == study_id).first()
    if not db_study:
        raise HTTPException(status_code=404, detail="Study not found")
    
    # Update fields if provided
    update_data = study_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "published" and value and not db_study.published:
            # Mark as published with timestamp
            from datetime import datetime, timezone
            db_study.published_at = datetime.now(timezone.utc)
        setattr(db_study, field, value)
    
    db.commit()
    db.refresh(db_study)
    
    study_response = schemas.WeeklyStudyResponse.model_validate(db_study)
    study_response.response_count = len([r for r in db_study.responses if not r.is_hidden])
    return study_response

@app.delete(f"{settings.api_prefix}/studies/{{study_id}}")
async def delete_weekly_study(study_id: int, db: Session = Depends(get_db)):
    """Delete a weekly study"""
    db_study = db.query(database.WeeklyStudy).filter(database.WeeklyStudy.id == study_id).first()
    if not db_study:
        raise HTTPException(status_code=404, detail="Study not found")
    
    db.delete(db_study)
    db.commit()
    return {"message": "Study deleted successfully"}

# Study Response Routes
@app.post(f"{settings.api_prefix}/studies/{{study_id}}/responses", response_model=schemas.StudyResponseResponse)
async def create_study_response(
    study_id: int,
    response: schemas.StudyResponseCreate,
    db: Session = Depends(get_db)
):
    """Create a new response to a study"""
    # Verify study exists and is published
    study = db.query(database.WeeklyStudy).filter(
        and_(
            database.WeeklyStudy.id == study_id,
            database.WeeklyStudy.published == True
        )
    ).first()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found or not published")
    
    db_response = database.StudyResponse(
        study_id=study_id,
        user_name=response.user_name.strip()[:100],  # Limit and clean name
        response_text=response.response_text.strip()
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    
    # Format response with empty reactions
    result = schemas.StudyResponseResponse.model_validate(db_response)
    result.reactions = []
    return result

@app.get(f"{settings.api_prefix}/studies/{{study_id}}/responses", response_model=List[schemas.StudyResponseResponse])
async def get_study_responses(
    study_id: int,
    skip: int = 0,
    limit: int = 100,
    user_identifier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get responses for a study"""
    responses = db.query(database.StudyResponse).filter(
        and_(
            database.StudyResponse.study_id == study_id,
            database.StudyResponse.is_hidden == False
        )
    ).order_by(database.StudyResponse.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for response in responses:
        # Get reaction summary for this response
        reactions_data = db.query(database.StudyReaction).filter(
            database.StudyReaction.response_id == response.id
        ).all()
        
        # Count reactions by type
        reaction_counts = Counter(r.reaction_type for r in reactions_data)
        user_reactions = set(r.reaction_type for r in reactions_data if r.user_identifier == user_identifier) if user_identifier else set()
        
        reaction_summaries = [
            schemas.ReactionSummary(
                reaction_type=reaction_type,
                count=count,
                user_reacted=reaction_type in user_reactions
            )
            for reaction_type, count in reaction_counts.items()
        ]
        
        response_data = schemas.StudyResponseResponse.model_validate(response)
        response_data.reactions = reaction_summaries
        result.append(response_data)
    
    return result

@app.put(f"{settings.api_prefix}/responses/{{response_id}}", response_model=schemas.StudyResponseResponse)
async def update_study_response(
    response_id: int,
    response_update: schemas.StudyResponseUpdate,
    db: Session = Depends(get_db)
):
    """Update a study response"""
    db_response = db.query(database.StudyResponse).filter(database.StudyResponse.id == response_id).first()
    if not db_response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    if response_update.response_text:
        db_response.response_text = response_update.response_text.strip()
    
    db.commit()
    db.refresh(db_response)
    
    result = schemas.StudyResponseResponse.model_validate(db_response)
    result.reactions = []  # Simplified for update response
    return result

@app.delete(f"{settings.api_prefix}/responses/{{response_id}}")
async def delete_study_response(response_id: int, db: Session = Depends(get_db)):
    """Delete a study response"""
    db_response = db.query(database.StudyResponse).filter(database.StudyResponse.id == response_id).first()
    if not db_response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    db.delete(db_response)
    db.commit()
    return {"message": "Response deleted successfully"}

# Study Reaction Routes
@app.post(f"{settings.api_prefix}/responses/{{response_id}}/reactions")
async def toggle_reaction(
    response_id: int,
    reaction: schemas.StudyReactionCreate,
    db: Session = Depends(get_db)
):
    """Toggle a reaction on a study response"""
    # Check if response exists
    response_exists = db.query(database.StudyResponse).filter(database.StudyResponse.id == response_id).first()
    if not response_exists:
        raise HTTPException(status_code=404, detail="Response not found")
    
    # Check if user already has this reaction
    existing_reaction = db.query(database.StudyReaction).filter(
        and_(
            database.StudyReaction.response_id == response_id,
            database.StudyReaction.user_identifier == reaction.user_identifier,
            database.StudyReaction.reaction_type == reaction.reaction_type
        )
    ).first()
    
    if existing_reaction:
        # Remove the reaction (toggle off)
        db.delete(existing_reaction)
        db.commit()
        return {"message": "Reaction removed", "action": "removed"}
    else:
        # Add the reaction (toggle on)
        db_reaction = database.StudyReaction(
            response_id=response_id,
            user_identifier=reaction.user_identifier,
            reaction_type=reaction.reaction_type
        )
        db.add(db_reaction)
        db.commit()
        return {"message": "Reaction added", "action": "added"}

# Community Guidelines Endpoint
@app.get(f"{settings.api_prefix}/community-guidelines", response_model=schemas.CommunityGuidelines)
async def get_community_guidelines():
    """Get community guidelines for respectful discussion"""
    return schemas.CommunityGuidelines()

# Moderation Routes (Admin)
@app.put(f"{settings.api_prefix}/responses/{{response_id}}/flag")
async def flag_response(response_id: int, db: Session = Depends(get_db)):
    """Flag a response for moderation"""
    db_response = db.query(database.StudyResponse).filter(database.StudyResponse.id == response_id).first()
    if not db_response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    db_response.is_flagged = True
    db.commit()
    return {"message": "Response flagged for review"}

@app.put(f"{settings.api_prefix}/responses/{{response_id}}/hide")
async def hide_response(response_id: int, db: Session = Depends(get_db)):
    """Hide a response (admin only)"""
    db_response = db.query(database.StudyResponse).filter(database.StudyResponse.id == response_id).first()
    if not db_response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    db_response.is_hidden = True
    db.commit()
    return {"message": "Response hidden"}

@app.get(f"{settings.api_prefix}/admin/flagged-responses", response_model=List[schemas.StudyResponseResponse])
async def get_flagged_responses(db: Session = Depends(get_db)):
    """Get all flagged responses for admin review"""
    flagged = db.query(database.StudyResponse).filter(database.StudyResponse.is_flagged == True).all()
    return [schemas.StudyResponseResponse.model_validate(r) for r in flagged]

# Scheduler Routes (Admin)
@app.post(f"{settings.api_prefix}/admin/publish-scheduled")
async def publish_scheduled_studies():
    """Manually trigger publishing of scheduled studies"""
    published_count = study_scheduler.publish_scheduled_studies()
    return {"message": f"Published {published_count} studies"}

@app.get(f"{settings.api_prefix}/admin/upcoming-studies")
async def get_upcoming_studies(limit: int = 10, db: Session = Depends(get_db)):
    """Get upcoming unpublished studies"""
    studies = study_scheduler.get_upcoming_studies(db, limit)
    result = []
    for study in studies:
        study_response = schemas.WeeklyStudyResponse.model_validate(study)
        study_response.response_count = 0  # Unpublished studies have no responses
        result.append(study_response)
    return result

@app.get(f"{settings.api_prefix}/admin/next-wednesday")
async def get_next_wednesday_date():
    """Get the next Wednesday date for scheduling"""
    next_wednesday = study_scheduler.get_next_wednesday()
    return {"next_wednesday": next_wednesday.isoformat()}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)