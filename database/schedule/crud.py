"""
Schedules:
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    weekday = Column(String(20), nullable=False)  # e.g., Monday, Tuesday
    time = Column(String(10), nullable=False)     # e.g., 14:00
    
    lessons = relationship("Lessons", backref="schedule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Schedule(student_id={self.student_id}, weekday={self.weekday}, time={self.time})>"
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import db
from database.models import Schedules
from datetime import datetime
from utils.config import Settings

logger = Settings.LOGGER

def create_schedule(student_id: int, weekday: str, time: str) -> Schedules:
    try: 
        session = db.get_session()
        new_schedule = Schedules(
            student_id=student_id,
            weekday=weekday,
            time=time
        )
        session.add(new_schedule)
        session.commit()
        logger.info(f"Created new schedule for student_id={student_id} on {weekday} at {time}")
        return new_schedule
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating schedule: {e}")
        raise e

def get_schedule(schedule_id: int) -> Schedules:
    try:
        session = db.get_session()
        logger.info(f"Retrieving schedule with id={schedule_id}")
        return session.query(Schedules).filter_by(id=schedule_id).first()
    except Exception as e:
        logger.error(f"Error getting schedule with id={schedule_id}: {e}")
        raise e

def get_schedules_by_student(student_id: int):
    try:
        session = db.get_session()
        logger.info(f"Retrieving schedules for student_id={student_id}")
        return session.query(Schedules).filter_by(student_id=student_id).all()
    except Exception as e:
        logger.error(f"Error getting schedules for student_id={student_id}: {e}")
        raise e

def get_all_schedules_for_weekday(weekday: str):
    try:
        session = db.get_session()
        logger.info(f"Retrieving schedules for weekday={weekday}")
        return session.query(Schedules).filter_by(weekday=weekday).all()
    except Exception as e:
        logger.error(f"Error getting schedules for weekday={weekday}: {e}")
        raise e

def get_all_schedules_by_date(date:datetime):
    pass
    

def update_schedule(schedule:Schedules) -> Schedules:
    try:
        session = db.get_session()
        session.commit()
        logger.info(f"Updated schedule with id={schedule.id}")
        return schedule
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating schedule with id={schedule.id}: {e}")
        raise e 

def delete_schedule(schedule_id: int) -> bool:
    try:
        schedule = get_schedule(schedule_id)
        if schedule:
            session = db.get_session()
            session.delete(schedule)
            session.commit()
            logger.info(f"Deleted schedule with id={schedule_id}")
            return True
        logger.warning(f"Schedule with id={schedule_id} not found for deletion")
        return False
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting schedule with id={schedule_id}: {e}")
        raise e