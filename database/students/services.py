from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import db
from datetime import datetime
from database.models import Students 
from utils.config import Settings
from database.models import Students
logger = Settings.LOGGER


def add_to_student_balance(student_id: int, amount: float) -> Students:
    try:
        session = db.get_session()
        student = session.query(Students).filter_by(id=student_id).first()
        if not student:
            raise ValueError(f"Student with id={student_id} not found.")
        student.balance += amount
        session.commit()
        logger.info(f"Added {amount} to student id={student_id}. New balance={student.balance}")
        return student
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding to student balance for id={student_id}: {e}")
        raise e
    
def subtract_from_student_balance(student_id: int, amount: float) -> Students:
    try:
        session = db.get_session()
        student = session.query(Students).filter_by(id=student_id).first()
        if not student:
            raise ValueError(f"Student with id={student_id} not found.")
        student.balance -= amount
        session.commit()
        logger.info(f"Subtracted {amount} from student id={student_id}. New balance={student.balance}")
        return student
    except Exception as e:
        session.rollback()
        logger.error(f"Error subtracting from student balance for id={student_id}: {e}")
        raise e