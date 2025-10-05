from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Bible API Schemas
class BibleVersion(BaseModel):
    id: str
    name: str
    language: str
    abbreviation: str
    description: Optional[str] = None

class VerseContent(BaseModel):
    id: str
    reference: str
    content: str
    
class SearchResult(BaseModel):
    verse: VerseContent
    bible_id: str
    bible_name: str

# Journal Entry Schemas
class JournalEntryCreate(BaseModel):
    verse_reference: str
    verse_text: str
    bible_version: str
    bible_id: str
    title: Optional[str] = None
    content: str
    tags: List[str] = []

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class JournalEntryResponse(BaseModel):
    id: int
    verse_reference: str
    verse_text: str
    bible_version: str
    bible_id: str
    title: Optional[str] = None
    content: str
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Favorite Verse Schemas
class FavoriteVerseCreate(BaseModel):
    verse_reference: str
    verse_text: str
    bible_version: str
    bible_id: str
    notes: Optional[str] = None

class FavoriteVerseResponse(BaseModel):
    id: int
    verse_reference: str
    verse_text: str
    bible_version: str
    bible_id: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Search Request Schema
class SearchRequest(BaseModel):
    query: str
    bible_id: Optional[str] = None
    limit: Optional[int] = 10