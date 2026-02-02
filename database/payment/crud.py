from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import db
from datetime import datetime
from database.models import Students 
from utils.config import Settings
from database.models import Payments
logger = Settings.LOGGER


def create_payment(student_id: int, amount: float, payment_date: datetime = None) -> Payments:
    try:
        session = db.get_session()
        if payment_date is None:
            payment_date = datetime.utcnow()
        new_payment = Payments(
            student_id=student_id,
            amount=amount,
            date=payment_date
        )
        session.add(new_payment)
        session.commit()
        logger.info(f"Created new payment for student_id={student_id}, amount={amount}")
        from database.students.services import add_to_student_balance
        add_to_student_balance(student_id, amount)
        logger.info(f"Updated balance for student_id={student_id} after payment")
        return new_payment
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating payment for student_id={student_id}: {e}")
        raise e
    
