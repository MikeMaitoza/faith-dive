"""
Weekly Study Scheduler Service

This service handles automatic publishing of weekly studies on Wednesdays.
Can be run as a background task or cron job.
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.models.database import WeeklyStudy
import logging

logger = logging.getLogger(__name__)

class StudyScheduler:
    def __init__(self):
        pass
    
    def publish_scheduled_studies(self):
        """
        Publish studies that are scheduled for today or earlier and not yet published.
        This should be run daily, preferably early Wednesday morning.
        """
        try:
            db = SessionLocal()
            try:
                now = datetime.now(timezone.utc)
                
                # Find studies that should be published
                studies_to_publish = db.query(WeeklyStudy).filter(
                    WeeklyStudy.published == False,
                    WeeklyStudy.scheduled_date <= now
                ).all()
                
                published_count = 0
                for study in studies_to_publish:
                    study.published = True
                    study.published_at = now
                    published_count += 1
                    logger.info(f"Published study: {study.title} (ID: {study.id})")
                
                if published_count > 0:
                    db.commit()
                    logger.info(f"Successfully published {published_count} studies")
                else:
                    logger.info("No studies to publish today")
                
                return published_count
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error publishing scheduled studies: {e}")
            return 0
    
    def get_next_wednesday(self, from_date: datetime = None) -> datetime:
        """
        Get the next Wednesday after the given date (or today).
        Useful for scheduling new studies.
        """
        if from_date is None:
            from_date = datetime.now(timezone.utc)
        
        # Find days until next Wednesday (weekday 2 = Wednesday)
        days_until_wednesday = (2 - from_date.weekday()) % 7
        if days_until_wednesday == 0 and from_date.hour >= 12:  # If it's Wednesday after noon, get next Wednesday
            days_until_wednesday = 7
        
        next_wednesday = from_date + timedelta(days=days_until_wednesday)
        # Set to 9 AM on Wednesday
        next_wednesday = next_wednesday.replace(hour=9, minute=0, second=0, microsecond=0)
        
        return next_wednesday
    
    def schedule_study_for_next_wednesday(self, db: Session, study: WeeklyStudy) -> datetime:
        """
        Automatically set the scheduled_date for a new study to next Wednesday.
        """
        next_wednesday = self.get_next_wednesday()
        study.scheduled_date = next_wednesday
        return next_wednesday
    
    def get_upcoming_studies(self, db: Session, limit: int = 5):
        """
        Get upcoming unpublished studies ordered by scheduled date.
        """
        return db.query(WeeklyStudy).filter(
            WeeklyStudy.published == False
        ).order_by(WeeklyStudy.scheduled_date.asc()).limit(limit).all()

# Create a global instance
study_scheduler = StudyScheduler()

# CLI function for running as a cron job
def main():
    """Main function for running scheduler as a script"""
    logging.basicConfig(level=logging.INFO)
    scheduler = StudyScheduler()
    published = scheduler.publish_scheduled_studies()
    print(f"Published {published} studies")

if __name__ == "__main__":
    main()