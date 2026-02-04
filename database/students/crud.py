"""
Student:
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    lesson_price = Column(Float, nullable=False)
    payment_frequency = Column(String(50), nullable=False) # e.g., monthly, weekly, per lesson
    balance = Column(Float, default=0.0)


    schedule = relationship("Schedules", backref="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(name={self.name}, surname={self.surname}, balance={self.balance})>"
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import db
from datetime import datetime
from database.models import Students 
from utils.config import Settings
from database.models import Students
logger = Settings.LOGGER

def create_student(name: str, surname: str, lesson_price: float, payment_frequency: str) -> Students:
    try:
        session = db.get_session()
        new_student = Students(
            name=name,
            surname=surname,
            lesson_price=lesson_price,
            payment_frequency=payment_frequency
        )
        session.add(new_student)
        session.commit()
        logger.info(f"Created new student: {new_student.name} {new_student.surname}")
        return new_student
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating student: {e}")
        raise e
    
def get_all_students() -> list[Students]:
    try:
        session = db.get_session()
        students = session.query(Students).order_by(Students.id).all()
        logger.info(f"Retrieved all students, count={len(students)}")
        return students
    except Exception as e:
        logger.error(f"Error retrieving all students: {e}")
        raise e

def get_student(student_id: int) -> Students:
    try:
        session = db.get_session()
        logger.info(f"Retrieving student with id={student_id}")
        return session.query(Students).filter_by(id=student_id).first()
    except Exception as e:
        logger.error(f"Error getting student with id={student_id}: {e}")
        raise e

#TODO: Need to be verified
def update_student(student:Students) -> Students:
    try:
        session = db.get_session()
        session.merge(student)
        session.commit()
        logger.info(f"Updated student with id={student.id}")
        return student
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating student with id={student.id}: {e}")
        raise e
    
def delete_student(student_id: int) -> bool:
    try:
        student = get_student(student_id)
        if student:
            session = db.get_session()
            session.delete(student)
            session.commit()
            logger.info(f"Deleted student with id={student_id}")
            return True
        logger.error(f"Student with id={student_id} not found for deletion")
        return False
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting student with id={student_id}: {e}")
        raise e