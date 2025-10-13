from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import func

Base = declarative_base()

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    verse_reference = Column(String(100), nullable=False)  # e.g., "John 3:16"
    verse_text = Column(Text, nullable=False)
    bible_version = Column(String(50), nullable=False)  # e.g., "NIV", "KJV"
    bible_id = Column(String(50), nullable=False)  # API Bible ID
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=list)  # Store as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<JournalEntry(id={self.id}, verse_reference='{self.verse_reference}', title='{self.title}')>"

class FavoriteVerse(Base):
    __tablename__ = "favorite_verses"
    
    id = Column(Integer, primary_key=True, index=True)
    verse_reference = Column(String(100), nullable=False)
    verse_text = Column(Text, nullable=False)
    bible_version = Column(String(50), nullable=False)
    bible_id = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<FavoriteVerse(id={self.id}, verse_reference='{self.verse_reference}')>"

class WeeklyStudy(Base):
    __tablename__ = "weekly_studies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    verse_references = Column(JSON, nullable=False)  # List of verse references
    verse_texts = Column(JSON, nullable=False)  # List of verse texts
    bible_version = Column(String(50), nullable=False)
    bible_id = Column(String(50), nullable=False)
    study_questions = Column(JSON, nullable=True)  # List of discussion questions
    study_notes = Column(Text, nullable=True)  # Admin notes/commentary
    scheduled_date = Column(DateTime(timezone=True), nullable=False)  # When to publish
    published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    responses = relationship("StudyResponse", back_populates="study", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WeeklyStudy(id={self.id}, title='{self.title}', scheduled_date='{self.scheduled_date}')>"

class StudyResponse(Base):
    __tablename__ = "study_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("weekly_studies.id"), nullable=False)
    user_name = Column(String(100), nullable=False)  # For now, simple name field
    response_text = Column(Text, nullable=False)
    is_flagged = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)  # For moderation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    study = relationship("WeeklyStudy", back_populates="responses")
    reactions = relationship("StudyReaction", back_populates="response", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<StudyResponse(id={self.id}, user_name='{self.user_name}', study_id={self.study_id})>"

class StudyReaction(Base):
    __tablename__ = "study_reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("study_responses.id"), nullable=False)
    user_identifier = Column(String(100), nullable=False)  # Could be name, email hash, or session ID
    reaction_type = Column(String(20), nullable=False)  # 'like', 'helpful', 'pray', 'amen'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    response = relationship("StudyResponse", back_populates="reactions")
    
    def __repr__(self):
        return f"<StudyReaction(id={self.id}, reaction_type='{self.reaction_type}', response_id={self.response_id})>"
