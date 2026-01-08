from sqlalchemy import select
from database import db
from database.models import CreditPayment
from sqlalchemy.orm import Session
from datetime import datetime
from utils.config import Settings

logger = Settings.LOGGER

def create_credit_payment(credit_id: int,
                                 payment_date: datetime,
                                 amount: float) -> CreditPayment:
    """Create a new future credit payment entry in the database"""
    session = db.get_session()
    new_payment = CreditPayment(
        credit_id=credit_id,
        payment_date=payment_date,
        amount=amount
    )
    session.add(new_payment)
    session.commit()
    session.refresh(new_payment)
    return new_payment

def get_monthly_credit_payments(credit_id: int) -> int:
    """Retrieve all future credit payments for a specific credit"""
    session = db.get_session()
    stmt = select(CreditPayment.amount).where(CreditPayment.credit_id == credit_id).order_by(CreditPayment.payment_date).limit(1)
    payments = session.execute(stmt).scalars().all()
    return payments[0]

def update_future_credit_payment(payment: CreditPayment):
    """Update a future credit payment entry in the database"""
    session = db.get_session()
    existing_payment = session.query(CreditPayment).filter(CreditPayment.id == payment.id).first()
    if existing_payment:
        existing_payment.payment_date = payment.payment_date
        existing_payment.amount = payment.amount
        session.commit()
        session.refresh(existing_payment)
    return existing_payment

