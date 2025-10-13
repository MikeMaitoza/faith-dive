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

# Weekly Study Schemas
class WeeklyStudyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    verse_references: List[str]  # ["John 3:16", "Romans 8:28"]
    verse_texts: List[str]       # Corresponding verse texts
    bible_version: str
    bible_id: str
    study_questions: Optional[List[str]] = []
    study_notes: Optional[str] = None
    scheduled_date: datetime

class WeeklyStudyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    verse_references: Optional[List[str]] = None
    verse_texts: Optional[List[str]] = None
    bible_version: Optional[str] = None
    bible_id: Optional[str] = None
    study_questions: Optional[List[str]] = None
    study_notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    published: Optional[bool] = None

class WeeklyStudyResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    verse_references: List[str]
    verse_texts: List[str]
    bible_version: str
    bible_id: str
    study_questions: List[str] = []
    study_notes: Optional[str] = None
    scheduled_date: datetime
    published: bool
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    response_count: Optional[int] = 0  # Will be computed
    
    model_config = ConfigDict(from_attributes=True)

# Study Response Schemas
class StudyResponseCreate(BaseModel):
    study_id: int
    user_name: str
    response_text: str

class StudyResponseUpdate(BaseModel):
    response_text: Optional[str] = None

class ReactionSummary(BaseModel):
    reaction_type: str
    count: int
    user_reacted: bool = False  # Whether current user has this reaction

class StudyResponseResponse(BaseModel):
    id: int
    study_id: int
    user_name: str
    response_text: str
    is_flagged: bool
    is_hidden: bool
    created_at: datetime
    updated_at: datetime
    reactions: List[ReactionSummary] = []
    
    model_config = ConfigDict(from_attributes=True)

# Study Reaction Schemas  
class StudyReactionCreate(BaseModel):
    response_id: int
    user_identifier: str  # Could be name, email hash, or session ID
    reaction_type: str    # 'like', 'helpful', 'pray', 'amen'

class StudyReactionResponse(BaseModel):
    id: int
    response_id: int
    user_identifier: str
    reaction_type: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Community Guidelines
class CommunityGuidelines(BaseModel):
    message: str = "Please be respectful of others thoughts and opinions. Not everyone sees these verses with the same lens."
    guidelines: List[str] = [
        "Share your thoughts with love and kindness",
        "Listen to understand, not to argue", 
        "Respect different interpretations and perspectives",
        "Keep discussions focused on the study topic",
        "Report any content that seems inappropriate"
    ]
