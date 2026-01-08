from database import db
from database.models import CreditPayment
from sqlalchemy import select, case, func
from sqlalchemy.orm import Session
from utils.config import Settings
from database.transactions.crud import create_transaction
from database.credit_payment.crud import get_monthly_credit_payments
from datetime import datetime
logger = Settings.LOGGER

def pay_next_credit_payment(credit_id: int):
    """Mark the next unpaid credit payment as paid"""
    session = db.get_session()
    try:
        # Find the next unpaid payment
        next_payment = session.query(CreditPayment).filter(
            CreditPayment.credit_id == credit_id,
            CreditPayment.status == False
        ).order_by(CreditPayment.payment_date).first()
        
        if next_payment:
            next_payment.status = True
            session.commit()
            logger.info(f"Marked payment ID {next_payment.id} as paid for credit ID {credit_id}")
            create_transaction(
                user_id=next_payment.credit.user_id,
                name=f"Credit Payment",
                shop=next_payment.credit.lender_name,
                amount=next_payment.amount,
                category=next_payment.credit.category,
                date=datetime.utcnow()
            )
            return next_payment
        else:
            logger.info(f"No unpaid payments found for credit ID {credit_id}")
            return None
    except Exception as e:
        logger.error(f"Error marking next payment as paid for credit ID {credit_id}: {e}")
        session.rollback()
        raise

def get_next_credit_payment(credit_id: int) -> CreditPayment:
    """Retrieve the next unpaid credit payment for a specific credit"""
    session = db.get_session()
    try:
        next_payment = session.query(CreditPayment).filter(
            CreditPayment.credit_id == credit_id,
            CreditPayment.status == False
        ).order_by(CreditPayment.payment_date).first()
        return next_payment
    except Exception as e:
        logger.error(f"Error retrieving next payment for credit ID {credit_id}: {e}")
        raise

def pay_full_credit(credit_id: int,amount: float):
    """Mark all unpaid credit payments as paid for a specific credit"""
    from database.credit.crud import get_credit_amount
    credit_amount = get_credit_amount(credit_id)
    session = db.get_session()
    try:
        unpaid_payments = session.query(CreditPayment).filter(
            CreditPayment.credit_id == credit_id,
            CreditPayment.status == False
        ).all()
        
        for payment in unpaid_payments:
            payment.status = True
        create_transaction(
            user_id=payment.credit.user_id,
            name=f"Credit Payment",
            shop=payment.credit.lender_name,
            amount=amount if amount else credit_amount,
            category=payment.credit.category,
            date=datetime.utcnow()
        )
        
        session.commit()
        logger.info(f"Marked {len(unpaid_payments)} payments as paid for credit ID {credit_id}")
        return len(unpaid_payments)
    except Exception as e:
        logger.error(f"Error marking all payments as paid for credit ID {credit_id}: {e}")
        session.rollback()
        raise



def pay_custom_credit_payment(credit_id: int, custom_amount: float):
    """Mark a specific credit payment as paid"""
    session = db.get_session()
    monthly_amount = get_monthly_credit_payments(credit_id)
    number = int(custom_amount // monthly_amount)
    remaining_amount = custom_amount-(monthly_amount*number)

    logger.info(f"Custom payment amount {custom_amount} covers {number} payments for credit ID {credit_id}")
    try:
        for _ in range(int(number)):
            next_payment = get_next_credit_payment(credit_id)
            if next_payment:
                next_payment.status = True
                session.commit()
                logger.info(f"Marked payment ID {next_payment.id} as paid for credit ID {credit_id}")
        next_payment = get_next_credit_payment(credit_id)
        if next_payment and remaining_amount > 0:
            next_payment.amount -= remaining_amount
            session.commit()
            logger.info(f"Reduced payment ID {next_payment.id} by {remaining_amount} for credit ID {credit_id}")
        create_transaction(
            user_id=next_payment.credit.user_id,
            name=f"Credit Payment",
            shop=next_payment.credit.lender_name,
            amount=custom_amount,
            category=next_payment.credit.category,
            date=datetime.utcnow()
        )
        return True
    except Exception as e:
        logger.error(f"Error processing custom payment for credit ID {credit_id}: {e}")
        session.rollback()
        raise