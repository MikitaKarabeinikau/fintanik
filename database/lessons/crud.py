"""
Lessons:
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('schedules.id'), nullable=False)
    paid = Column(Boolean, default=False)
    complited = Column(Boolean, default=False)
    date = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<Lesson(schedule_id={self.schedule_id}, date={self.date}, paid={self.paid}, complited={self.complited})>"
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import db
from database.models import Lessons, Schedules, Students
from datetime import datetime
from utils.config import Settings

logger = Settings.LOGGER

def create_lesson(schedule_id: int, date: datetime, paid: bool = False, complited: bool = False) -> Lessons:
    try:
        session = db.get_session()
        new_lesson = Lessons(
            schedule_id=schedule_id,
            date=date,
            paid=paid,
            complited=complited
        )
        session.add(new_lesson)
        session.commit()
        logger.info(f"Created new lesson for schedule_id={schedule_id} on {date}")
        return new_lesson
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating lesson: {e}")
        raise e
    
    
def get_lesson(lesson_id: int) -> Lessons:
    try:
        session = db.get_session()
        logger.info(f"Retrieving lesson with id={lesson_id}")
        return session.query(Lessons).filter_by(id=lesson_id).first()
    except Exception as e:
        logger.error(f"Error getting lesson with id={lesson_id}: {e}")
        raise e


    

def get_all_lessons_by_day(date: datetime):
    try:
        session = db.get_session()
        logger.info(f"Retrieving lessons for date={date.date()}")
        start_of_day = datetime.combine(date.date(), datetime.min.time())
        end_of_day = datetime.combine(date.date(), datetime.max.time())
        return session.query(Lessons).filter(Lessons.date >= start_of_day, Lessons.date <= end_of_day).all()
    except Exception as e:
        logger.error(f"Error getting lessons for date={date.date()}: {e}")
        raise e
    
def update_lesson(lesson: Lessons) -> Lessons:
    try:
        session = db.get_session()
        session.merge(lesson)
        session.commit()
        logger.info(f"Updated lesson with id={lesson.id}")
        return lesson
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating lesson with id={lesson.id}: {e}")
        raise e
    
def delete_lesson(lesson_id: int) -> bool:
    try:
        lesson = get_lesson(lesson_id)
        if lesson:
            session = db.get_session()
            session.delete(lesson)
            session.commit()
            logger.info(f"Deleted lesson with id={lesson_id}")
            return True
        logger.warning(f"Lesson with id={lesson_id} not found for deletion")
        return False
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting lesson with id={lesson_id}: {e}")
        raise e