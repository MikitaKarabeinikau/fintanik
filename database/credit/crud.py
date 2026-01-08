from sqlalchemy import select
from database import db
from database.models import Credit
from sqlalchemy.orm import Session
from datetime import datetime
from utils.config import Settings

logger = Settings.LOGGER

def create_credit(user_id: int,
                  lender_name: str,
                  total_amount:float,
                  monthly_payment: float,
                  last_payment: float,
                  start_date: datetime,
                  end_date: datetime,
                last_payment_amount: float,
                  category: str = "Credit",
                  paid: bool = False) -> Credit:
    """Create a new credit entry in the database"""
    session = db.get_session()
    new_credit = Credit(
        user_id=user_id,
        lender_name=lender_name,
        total_amount=total_amount,
        monthly_payment=monthly_payment,
        category=category,
        start_date=start_date,
        end_date=end_date,
        last_payment_amount=last_payment_amount,
        paid=paid
    )
    session.add(new_credit)
    session.commit()
    session.refresh(new_credit)
    return new_credit

def update_credit_payment(credit: Credit):
    """Update the last payment date and amount for a credit"""
    session = db.get_session()
    existing_credit = session.query(Credit).filter(Credit.id == credit.id).first()
    if existing_credit:
        existing_credit.total = credit.total
        existing_credit.monthly_payment = credit.monthly_payment
        existing_credit.category = credit.category
        existing_credit.lender_name = credit.lender_name
        existing_credit.last_payment_date = credit.last_payment_date
        existing_credit.last_payment_amount = credit.last_payment_amount
        existing_credit.paid = credit.paid
        session.commit()
        session.refresh(existing_credit)
    return existing_credit

def get_credits() -> list[Credit]:
    """Retrieve all credit entries from the database"""
    session = db.get_session()
    stmt = select(Credit)
    credits = session.execute(stmt).scalars().all()
    return credits

def delete_credit(credit_id: int) -> bool:
    """Delete a credit entry and all its payments from the database"""
    from database.models import CreditPayment
    session = db.get_session()
    try:
        # First, delete all related credit payments
        stmt_payments = select(CreditPayment).filter(CreditPayment.credit_id == credit_id)
        payments = session.execute(stmt_payments).scalars().all()
        for payment in payments:
            session.delete(payment)
        
        # Then delete the credit
        stmt_credit = select(Credit).filter(Credit.id == credit_id)
        credit_to_delete = session.execute(stmt_credit).scalar_one_or_none()
        if credit_to_delete:
            session.delete(credit_to_delete)
            session.commit()
            logger.info(f"Deleted credit {credit_id} and {len(payments)} related payments")
            return True
        return False
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting credit {credit_id}: {e}")
        raise

def get_credit_amount(credit_id: int) -> float:
    """Retrieve the total amount for a specific credit"""
    session = db.get_session()
    credit = session.query(Credit).filter(Credit.id == credit_id).first()
    if credit:
        return credit.total_amount
    return 0.0