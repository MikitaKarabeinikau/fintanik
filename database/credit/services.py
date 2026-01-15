from sqlalchemy import func, update, select, case
from database import db
from database.credit_payment.services import get_next_credit_payment
from database.models import Credit
from sqlalchemy.orm import Session
from datetime import datetime
from utils.config import Settings
from database.credit_payment.crud import create_credit_payment
logger = Settings.LOGGER
from database.models import CreditPayment

def fill_credit_payments(credit: Credit):
    """Fill in future credit payments based on the credit details"""
    session = db.get_session()
    try:
        payment_date = credit.start_date
        
        while payment_date < credit.end_date:  # Changed <= to < so we handle end_date separately
            new_payment = create_credit_payment(
                credit_id=credit.id,
                payment_date=payment_date,
                amount=credit.monthly_payment
            )
            session.add(new_payment)
            
            # Move to next month
            if payment_date.month == 12:
                payment_date = payment_date.replace(year=payment_date.year + 1, month=1)
            else:
                payment_date = payment_date.replace(month=payment_date.month + 1)
        
        # Create final payment on end_date with last_payment_amount
        final_payment = create_credit_payment(
            credit_id=credit.id,
            payment_date=credit.end_date,
            amount=credit.last_payment_amount
        )
        session.add(final_payment)
        
        session.commit()
        logger.info(f"Successfully created {payment_date} payments for credit ID {credit.id}")
    except Exception as e:
        logger.error(f"Error filling credit payments for credit ID {credit.id}: {e}")
        session.rollback()
        raise

def get_unpaid_credit_payments_dict():
    """Get unpaid credit payments as list of dictionaries"""
    session = db.get_session()
    try:
        stmt = select(
            Credit.lender_name,
            Credit.category,
            CreditPayment.amount,
            CreditPayment.payment_date,
            CreditPayment.credit_id
        ).join(
            CreditPayment,
            Credit.id == CreditPayment.credit_id
        ).where(
            CreditPayment.status == False
        ).distinct(
            CreditPayment.credit_id
        ).order_by(
            CreditPayment.credit_id,
            CreditPayment.payment_date.asc()
        )
        results = session.execute(stmt).all()
        
        # Convert to list of dictionaries
        payments = []
        for row in results:
            payments.append({
                'lender_name': row.lender_name,
                'category': row.category,
                'amount': row.amount,
                'payment_date': row.payment_date
            })
        
        # Sort the final list by payment_date
        payments.sort(key=lambda x: x['payment_date'])
        
        return payments
    except Exception as e:
        logger.error(f"Error getting unpaid credit payments: {e}")
        raise

def get_credit_statistics():
    """Get comprehensive statistics about all credits"""
    from database.models import Credit, CreditPayment
    from sqlalchemy import func
    
    session = db.get_session()
    try:
        # Get all credits with calculated statistics
        stmt = select(
            Credit.id,
            Credit.lender_name,
            Credit.category,
            Credit.total_amount,
            Credit.monthly_payment,
            Credit.start_date,
            Credit.end_date,
            Credit.last_payment_amount,
            # Count total payments
            func.count(CreditPayment.id).label('total_payments'),
            # Count paid payments
            func.sum(case(
                (CreditPayment.status == True, 1),
                else_=0
            )).label('paid_payments'),
            # Sum of paid amounts
            func.coalesce(func.sum(case(
                (CreditPayment.status == True, CreditPayment.amount),
                else_=0
            )), 0).label('total_paid'),
            # Sum of remaining payments
            func.sum(case(
                (CreditPayment.status == False, CreditPayment.amount),
                else_=0
            )).label('remaining_amount'),
            # Next payment date (earliest unpaid)
            func.min(case(
                (CreditPayment.status == False, CreditPayment.payment_date),
                else_=None
            )).label('next_payment_date')
        ).outerjoin(
            CreditPayment,
            Credit.id == CreditPayment.credit_id
        ).group_by(
            Credit.id,
            Credit.lender_name,
            Credit.category,
            Credit.total_amount,
            Credit.monthly_payment,
            Credit.start_date,
            Credit.end_date,
            Credit.last_payment_amount
        ).order_by(
            Credit.lender_name
        )
        
        results = session.execute(stmt).all()
        
        # Convert to list of dictionaries
        statistics = []
        for row in results:
            statistics.append({
                'id': row.id,
                'lender_name': row.lender_name,
                'category': row.category,
                'total_amount': row.total_amount,
                'monthly_payment': row.monthly_payment,
                'start_date': row.start_date,
                'end_date': row.end_date,
                'last_payment_amount': row.last_payment_amount,
                'total_payments': row.total_payments or 0,
                'paid_payments': row.paid_payments or 0,
                'total_paid': row.total_paid or 0.0,
                'remaining_amount': row.remaining_amount or 0.0,
                'next_payment_date': row.next_payment_date,
                'progress_percent': (row.paid_payments / row.total_payments * 100) if row.total_payments else 0,
                'next_payment_amount': get_next_credit_payment(row.id).amount if get_next_credit_payment(row.id) else 0.0
            })
        
        return statistics
    except Exception as e:
        logger.error(f"Error getting credit statistics: {e}")
        raise
    finally:
        session.close()


def get_overall_credit_summary():
    """Get overall summary of all credits"""
    from database.models import Credit, CreditPayment
    from sqlalchemy import func
    
    session = db.get_session()
    try:
        # Get total credits and total borrowed WITHOUT joining payments
        credit_summary = session.execute(
            select(
                func.count(Credit.id).label('total_credits'),
                func.sum(Credit.total_amount).label('total_borrowed')
            )
        ).one()
        
        # Get payment totals separately
        payment_summary = session.execute(
            select(
                func.sum(case(
                    (CreditPayment.status == True, CreditPayment.amount),
                    else_=0
                )).label('total_paid'),
                func.sum(case(
                    (CreditPayment.status == False, CreditPayment.amount),
                    else_=0
                )).label('total_remaining')
            )
        ).one()
        
        total_borrowed = credit_summary.total_borrowed or 0.0
        total_paid = payment_summary.total_paid or 0.0
        
        return {
            'total_credits': credit_summary.total_credits or 0,
            'total_borrowed': total_borrowed,
            'total_paid': total_paid,
            'total_remaining': payment_summary.total_remaining or 0.0,
            'progress_percent': (total_paid / total_borrowed * 100) if total_borrowed else 0
        }
    except Exception as e:
        logger.error(f"Error getting overall credit summary: {e}")
        raise
    finally:
        session.close()