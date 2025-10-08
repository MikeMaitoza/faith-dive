import pytest
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.models.database import JournalEntry, FavoriteVerse
from backend.models.schemas import JournalEntryCreate, FavoriteVerseCreate


class TestJournalEntryModel:
    """Test JournalEntry database model."""
    
    @pytest.mark.models
    @pytest.mark.database
    def test_journal_entry_creation(self, test_db):
        """Test creating a journal entry with all fields."""
        entry = JournalEntry(
            verse_reference="John 3:16",
            verse_text="For God so loved the world...",
            bible_version="NIV",
            bible_id="eng-NIV",
            title="God's Love",
            content="This verse shows God's amazing love.",
            tags=["love", "salvation", "eternal life"]
        )
        
        test_db.add(entry)
        test_db.commit()
        test_db.refresh(entry)
        
        assert entry.id is not None
        assert entry.verse_reference == "John 3:16"
        assert entry.title == "God's Love"
        assert len(entry.tags) == 3
        assert "love" in entry.tags
        assert entry.created_at is not None
        assert entry.updated_at is not None
    
    @pytest.mark.models
    @pytest.mark.database
    def test_journal_entry_minimal_fields(self, test_db):
        """Test creating a journal entry with minimal required fields."""
        entry = JournalEntry(
            verse_reference="Romans 8:28",
            verse_text="And we know that in all things...",
            bible_version="ESV",
            bible_id="eng-ESV",
            content="God works for our good."
        )
        
        test_db.add(entry)
        test_db.commit()
        test_db.refresh(entry)
        
        assert entry.id is not None
        assert entry.title is None
        assert entry.tags == []
        assert entry.created_at is not None
    
    @pytest.mark.models
    @pytest.mark.database
    def test_journal_entry_missing_required_field(self, test_db):
        """Test that missing required fields raise an error."""
        with pytest.raises((IntegrityError, ValueError)):
            entry = JournalEntry(
                verse_reference="John 3:16",
                # Missing verse_text (required)
                bible_version="NIV",
                bible_id="eng-NIV",
                content="This should fail."
            )
            test_db.add(entry)
            test_db.commit()
    
    @pytest.mark.models
    @pytest.mark.database
    def test_journal_entry_tags_as_json(self, test_db):
        """Test that tags are properly stored and retrieved as JSON."""
        tags = ["faith", "hope", "love", "prayer", "study"]
        
        entry = JournalEntry(
            verse_reference="1 Corinthians 13:13",
            verse_text="And now these three remain...",
            bible_version="NIV",
            bible_id="eng-NIV",
            content="The greatest of these is love.",
            tags=tags
        )
        
        test_db.add(entry)
        test_db.commit()
        test_db.refresh(entry)
        
        # Verify tags are stored and retrieved correctly
        assert entry.tags == tags
        assert isinstance(entry.tags, list)
        assert len(entry.tags) == 5
    
    @pytest.mark.models
    @pytest.mark.database
    def test_journal_entry_timestamps_auto_update(self, test_db):
        """Test that timestamps are automatically set and updated."""
        entry = JournalEntry(
            verse_reference="Psalm 23:1",
            verse_text="The Lord is my shepherd...",
            bible_version="NIV",
            bible_id="eng-NIV",
            content="God is my shepherd."
        )
        
        test_db.add(entry)
        test_db.commit()
        test_db.refresh(entry)
        
        original_created = entry.created_at
        original_updated = entry.updated_at
        
        # Update the entry
        entry.content = "Updated reflection on God's care."
        test_db.commit()
        test_db.refresh(entry)
        
        # created_at should remain the same, updated_at should change
        assert entry.created_at == original_created
        assert entry.updated_at >= original_updated
    
    @pytest.mark.models
    @pytest.mark.database
    def test_journal_entry_unicode_content(self, test_db):
        """Test that unicode content is properly stored."""
        entry = JournalEntry(
            verse_reference="John 1:1",
            verse_text="Ἐν ἀρχῇ ἦν ὁ λόγος",  # Greek text
            bible_version="NA28",
            bible_id="grc-NA28",
            content="In the beginning was the Word... ✝️ 🙏",
            tags=["Greek", "logos", "beginning"]
        )
        
        test_db.add(entry)
        test_db.commit()
        test_db.refresh(entry)
        
        assert "ἦν" in entry.verse_text
        assert "✝️" in entry.content
        assert "Greek" in entry.tags


class TestFavoriteVerseModel:
    """Test FavoriteVerse database model."""
    
    @pytest.mark.models
    @pytest.mark.database
    def test_favorite_verse_creation(self, test_db):
        """Test creating a favorite verse with all fields."""
        favorite = FavoriteVerse(
            verse_reference="Philippians 4:13",
            verse_text="I can do all this through him who gives me strength.",
            bible_version="NIV",
            bible_id="eng-NIV",
            notes="My strength comes from Christ."
        )
        
        test_db.add(favorite)
        test_db.commit()
        test_db.refresh(favorite)
        
        assert favorite.id is not None
        assert favorite.verse_reference == "Philippians 4:13"
        assert favorite.notes is not None
        assert favorite.created_at is not None
    
    @pytest.mark.models
    @pytest.mark.database
    def test_favorite_verse_without_notes(self, test_db):
        """Test creating a favorite verse without notes."""
        favorite = FavoriteVerse(
            verse_reference="Romans 8:28",
            verse_text="And we know that in all things...",
            bible_version="ESV",
            bible_id="eng-ESV"
        )
        
        test_db.add(favorite)
        test_db.commit()
        test_db.refresh(favorite)
        
        assert favorite.id is not None
        assert favorite.notes is None
        assert favorite.created_at is not None
    
    @pytest.mark.models
    @pytest.mark.database
    def test_favorite_verse_long_notes(self, test_db):
        """Test favorite verse with very long notes."""
        long_notes = "This is a very meaningful verse to me. " * 100  # Very long text
        
        favorite = FavoriteVerse(
            verse_reference="Isaiah 41:10",
            verse_text="So do not fear, for I am with you...",
            bible_version="NIV",
            bible_id="eng-NIV",
            notes=long_notes
        )
        
        test_db.add(favorite)
        test_db.commit()
        test_db.refresh(favorite)
        
        assert favorite.notes == long_notes
        assert len(favorite.notes) > 1000


class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    @pytest.mark.models
    def test_journal_entry_create_schema_valid(self):
        """Test valid journal entry creation schema."""
        data = {
            "verse_reference": "John 3:16",
            "verse_text": "For God so loved the world...",
            "bible_version": "NIV",
            "bible_id": "eng-NIV",
            "title": "God's Love",
            "content": "This verse demonstrates God's incredible love.",
            "tags": ["love", "salvation"]
        }
        
        schema = JournalEntryCreate(**data)
        
        assert schema.verse_reference == "John 3:16"
        assert schema.title == "God's Love"
        assert len(schema.tags) == 2
    
    @pytest.mark.models
    def test_journal_entry_create_schema_minimal(self):
        """Test minimal valid journal entry creation schema."""
        data = {
            "verse_reference": "Romans 8:28",
            "verse_text": "And we know that in all things...",
            "bible_version": "ESV",
            "bible_id": "eng-ESV",
            "content": "God works for our good."
        }
        
        schema = JournalEntryCreate(**data)
        
        assert schema.title is None
        assert schema.tags == []
    
    @pytest.mark.models
    def test_journal_entry_create_schema_missing_field(self):
        """Test journal entry schema with missing required field."""
        data = {
            "verse_reference": "John 3:16",
            "bible_version": "NIV",
            "content": "Missing verse_text and bible_id"
        }
        
        with pytest.raises(ValueError):
            JournalEntryCreate(**data)
    
    @pytest.mark.models
    def test_favorite_verse_create_schema_valid(self):
        """Test valid favorite verse creation schema."""
        data = {
            "verse_reference": "Philippians 4:13",
            "verse_text": "I can do all this through him...",
            "bible_version": "NIV",
            "bible_id": "eng-NIV",
            "notes": "Great encouragement verse"
        }
        
        schema = FavoriteVerseCreate(**data)
        
        assert schema.verse_reference == "Philippians 4:13"
        assert schema.notes == "Great encouragement verse"
    
    @pytest.mark.models
    def test_favorite_verse_create_schema_without_notes(self):
        """Test favorite verse schema without optional notes."""
        data = {
            "verse_reference": "1 Corinthians 13:4",
            "verse_text": "Love is patient, love is kind...",
            "bible_version": "ESV",
            "bible_id": "eng-ESV"
        }
        
        schema = FavoriteVerseCreate(**data)
        
        assert schema.notes is None


class TestDatabaseOperations:
    """Test database operations and constraints."""
    
    @pytest.mark.models
    @pytest.mark.database
    def test_database_connection(self, test_db):
        """Test that database connection works."""
        result = test_db.execute(text("SELECT 1")).fetchone()
        assert result[0] == 1
    
    @pytest.mark.models
    @pytest.mark.database
    def test_journal_entries_query(self, test_db, journal_entry_factory):
        """Test querying journal entries."""
        # Create test data
        entries = journal_entry_factory.create_batch(5)
        
        # Query all entries
        all_entries = test_db.query(JournalEntry).all()
        assert len(all_entries) == 5
        
        # Query with filter
        filtered_entries = test_db.query(JournalEntry).filter(
            JournalEntry.bible_version == entries[0].bible_version
        ).all()
        assert len(filtered_entries) >= 1
    
    @pytest.mark.models
    @pytest.mark.database
    def test_favorite_verses_query(self, test_db, favorite_verse_factory):
        """Test querying favorite verses."""
        # Create test data
        favorites = favorite_verse_factory.create_batch(3)
        
        # Query all favorites
        all_favorites = test_db.query(FavoriteVerse).all()
        assert len(all_favorites) == 3
        
        # Query specific favorite
        specific_favorite = test_db.query(FavoriteVerse).filter(
            FavoriteVerse.id == favorites[0].id
        ).first()
        assert specific_favorite is not None
        assert specific_favorite.id == favorites[0].id
    
    @pytest.mark.models
    @pytest.mark.database
    def test_database_rollback(self, test_db):
        """Test database rollback functionality."""
        # Create an entry
        entry = JournalEntry(
            verse_reference="Test Verse",
            verse_text="Test text",
            bible_version="TEST",
            bible_id="test",
            content="Test content"
        )
        
        test_db.add(entry)
        test_db.flush()  # Flush but don't commit
        
        # Entry should be in the session
        assert entry.id is not None
        
        # Rollback the transaction
        test_db.rollback()
        
        # Entry should not be in database after rollback
        count = test_db.query(JournalEntry).count()
        assert count == 0
    
    @pytest.mark.models
    @pytest.mark.database
    def test_cascade_operations(self, test_db):
        """Test that database operations work correctly with relationships."""
        # Note: This test assumes future relationship implementations
        # Currently our models don't have relationships, but this tests the concept
        
        # Create multiple entries
        entries = []
        for i in range(3):
            entry = JournalEntry(
                verse_reference=f"Test {i+1}:1",
                verse_text=f"Test text {i+1}",
                bible_version="TEST",
                bible_id="test",
                content=f"Test content {i+1}"
            )
            test_db.add(entry)
            entries.append(entry)
        
        test_db.commit()
        
        # Verify all entries exist
        count = test_db.query(JournalEntry).count()
        assert count == 3
        
        # Delete all test entries
        test_db.query(JournalEntry).filter(
            JournalEntry.bible_version == "TEST"
        ).delete()
        test_db.commit()
        
        # Verify deletion
        count = test_db.query(JournalEntry).count()
        assert count == 0
    
    @pytest.mark.models
    @pytest.mark.database
    @pytest.mark.parametrize("batch_size", [1, 5, 10, 50])
    def test_bulk_operations(self, test_db, journal_entry_factory, batch_size):
        """Test bulk database operations with different batch sizes."""
        # Create entries in bulk
        entries = journal_entry_factory.create_batch(batch_size)
        
        # Verify all entries were created
        count = test_db.query(JournalEntry).count()
        assert count == batch_size
        
        # Test bulk update
        test_db.query(JournalEntry).update({"bible_version": "BULK_TEST"})
        test_db.commit()
        
        # Verify update
        updated_count = test_db.query(JournalEntry).filter(
            JournalEntry.bible_version == "BULK_TEST"
        ).count()
        assert updated_count == batch_size