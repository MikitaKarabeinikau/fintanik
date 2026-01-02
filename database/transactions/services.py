from sqlalchemy import func, select
from database.db import db
from database.models import Transaction
from sqlalchemy.orm import Session
import logging
from datetime import date, datetime, timedelta,time
from database.models import Transaction,Account

logger = logging.getLogger(__name__)

def get_all_categories_from_account(account_name, session: Session):
    """Retrieve all unique categories from transactions for a specific account"""
    try:
        categories = session.query(Transaction.category).join(Account, Transaction.account_id == Account.id).filter(
            Account.name == account_name
        ).distinct().all()
        return [category[0] for category in categories]
    except Exception as e:
        logger.error(f"Error retrieving categories for account '{account_name}': {e}")
        raise

def get_user_shops_from_account(account_name, session: Session):
    """Retrieve all unique shops from transactions for a specific account"""
    try:
        shops = session.query(Transaction.shop).join(Account, Transaction.account_id == Account.id).filter(
            Account.name == account_name
        ).distinct().all()
        return [shop[0] for shop in shops if shop[0] is not None]
    except Exception as e:
        logger.error(f"Error retrieving shops for account '{account_name}': {e}")
        raise

def get_all_categories(session: Session):
    """Retrieve all unique categories from transactions"""
    try:
        categories = session.query(Transaction.category).distinct().all()
        return [category[0] for category in categories]
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        raise

def get_spendings_grouped(account: str, group_by: str, start_date: datetime, end_date: datetime, session: Session):
    """Retrieve spendings grouped by category or shop with totals"""
    try:
        # Determine which column to group by
        if group_by.lower() == 'category':
            group_column = Transaction.category
        elif group_by.lower() == 'shop':
            group_column = Transaction.shop
        else:
            raise ValueError(f"Invalid group_by value: {group_by}. Must be 'category' or 'shop'")
        
        # Query with grouping and aggregation
        stmt = select(
            group_column,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).join(
            Account, Transaction.account_id == Account.id
        ).where(
            Transaction.date.between(start_date, end_date),
            Account.name == account
        ).group_by(
            group_column
        ).order_by(
            func.sum(Transaction.amount).desc()
        )
        
        results = session.execute(stmt).all()
        return results  # Returns list of tuples: [(category/shop, total, count), ...]
    except Exception as e:
        logger.error(f"Error retrieving grouped spendings for account '{account}' by {group_by} between {start_date} and {end_date}: {e}")
        raise

def get_spendings(account: str, start_date: datetime, end_date: datetime, session: Session):
    """Retrieve spendings for a given account and date range"""
    try:
        start_of_day = start_date
        end_of_day = end_date
        
        stmt = select(Transaction).join(Account, Transaction.account_id == Account.id).where(Transaction.date.between(start_of_day, end_of_day)).where(Account.name == account)
        transactions = session.execute(stmt).scalars().all()
        return transactions
    except Exception as e:
        logger.error(f"Error retrieving spendings for account '{account}' between {start_date} and {end_date}: {e}")
        raise
        
        
    except Exception as e:
        logger.error(f"Error retrieving spendings for account '{account}' on {date}: {e}")
        raise

