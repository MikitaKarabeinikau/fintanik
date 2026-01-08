from sqlalchemy import update, select
from database.db import get_session
from database.models import Credit
from sqlalchemy.orm import Session
from datetime import datetime
from utils.config import Settings
from database.credit.crud import create_credit, update_credit_payment
logger = Settings.LOGGER


def get_last_credit_transaction(credit_id: int) -> Credit:
    """Retrieve the last credit transaction for a given credit ID"""
    try:
        session = get_session()
        stmt = select(Credit).where(Credit.id == credit_id).order_by(Credit.date.desc()).limit(1)
        result = session.execute(stmt).scalar_one_or_none()
        logger.debug(f"Retrieved last credit transaction for credit_id {credit_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving last credit transaction for credit_id {credit_id}: {e}")
        raise



def fill_credit_due_last_payment_dates(credit_id: int):
    """Fill in missing last payment dates for credits"""
    try:
        session = get_session()
        last_record = get_last_credit_transaction(credit_id)
        last_record_date = last_record.last_payment_date
        last_payment_date = last_record.last_payment_date
        logger.debug(f"Filling last payment date for credit_id {credit_id} with date {last_record_date}")
        while last_record_date.year <= last_payment_date.year and last_record_date.month+1 < last_payment_date.month:
            if last_record_date.month == 12:
                last_record_date = datetime(last_record_date.year + 1, 1, last_record_date.day)
            else:
                last_record_date = datetime(last_record_date.year, last_record_date.month + 1, last_record_date.day)
            logger.debug(f"Creating credit entry for missing payment date: {last_record_date}")
            create_credit(
                user_id=last_record.user_id,
                lender_name=last_record.lender_name,
                total=last_record.total-last_record.monthly_payment,
                date = last_record_date,
                monthly_payment=last_record.monthly_payment,
                last_payment_date=last_record_date,
                category=last_record.category,
                last_payment_amount=last_record.last_payment_amount,
                paid=False
            )
        create_credit(
            user_id=last_record.user_id,
            lender_name=last_record.lender_name,
            total=0.0,
            date = last_payment_date,
            monthly_payment=last_record.last_payment_amount,
            last_payment_date=last_payment_date,
            category=last_record.category,
            last_payment_amount=last_record.last_payment_amount,
            paid=False)
        logger.debug(f"Completed filling last payment dates for credit_id {credit_id}")
    except Exception as e:
        logger.error(f"Error filling last payment dates for credit_id {credit_id}: {e}")
        raise

def pay_monthly_credit_standart(credit_id:int):
    try:
        session = get_session()
        stmt = select(Credit).where(Credit.id == credit_id, Credit.paid == False).order_by(Credit.date.asc()).limit(1)
        credit = session.execute(stmt).scalar_one_or_none()
        if credit:
            credit.paid = True
            update_credit_payment(credit)
            logger.debug(f"Marked credit_id {credit_id} as paid for date {credit.date}")
            return credit
        else:
            logger.debug(f"No unpaid credit found for credit_id {credit_id}")
            return None
    except Exception as e:
        logger.error(f"Error marking credit_id {credit_id} as paid: {e}")
        raise

def pay_monthly_credit_advanced(credit_id:int, payment_amount: float):
    try:
        session = get_session()
        stmt = select(Credit).where(Credit.id == credit_id, Credit.paid == False).order_by(Credit.date.asc())
        credit = session.execute(stmt).scalar_one_or_none()
        for record in credit:
            if payment_amount <= record.monthly_payment:
                record.p
                payment_amount -= record.monthly_payment
                logger.debug(f"Marked credit_id {credit_id} as paid for date {record.date} with amount {record.monthly_payment}")