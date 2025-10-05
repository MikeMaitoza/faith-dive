from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base
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
