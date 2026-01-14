from sqlalchemy import func, select
from database.db import db
from database.models import Transaction
from sqlalchemy.orm import Session
import logging
from datetime import date, datetime, timedelta,time
from database.models import Transaction

logger = logging.getLogger(__name__)

def get_all_categories_from_account():
    """Retrieve all unique categories from transactions for a specific account"""
    try:
        session = db.get_session()
        categories = session.query(Transaction.category).distinct().all()
        return [category[0] for category in categories]
    except Exception as e:
        logger.error(f"Error retrieving categories ': {e}")
        raise

def get_user_shops_from_account():
    """Retrieve all unique shops from transactions for a specific account"""
    try:
        session = db.get_session()
        shops = session.query(Transaction.shop).distinct().all()
        return [shop[0] for shop in shops if shop[0] is not None]
    except Exception as e:
        logger.error(f"Error retrieving shops for account: {e}")
        raise

def get_all_categories():
    """Retrieve all unique categories from transactions"""
    try:
        session = db.get_session()
        categories = session.query(Transaction.category).distinct().all()
        return [category[0] for category in categories]
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        raise

def get_spendings_grouped( group_by: str, start_date: datetime, end_date: datetime):
    """Retrieve spendings grouped by category or shop with totals"""
    try:
        session = db.get_session()
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
        ).where(
            Transaction.date.between(start_date, end_date)
        ).group_by(
            group_column
        ).order_by(
            func.sum(Transaction.amount).desc()
        )
        
        results = session.execute(stmt).all()
        return results  # Returns list of tuples: [(category/shop, total, count), ...]
    except Exception as e:
        logger.error(f"Error retrieving grouped spendings by {group_by} between {start_date} and {end_date}: {e}")
        raise

def get_sorted_categories_by_popularity():
    """Retrieve categories sorted by popularity (number of transactions)"""
    try:
        session = db.get_session()
        stmt = select(
            Transaction.category,
            func.count(Transaction.id).label('transaction_count')
        ).group_by(
            Transaction.category
        ).order_by(
            func.count(Transaction.id).desc()
        )
        
        results = session.execute(stmt).all()
        logger.debug(f"Sorted categories by popularity: {results}")
        print(f"DEBUG: Sorted categories results = {results}")
        result = [category for category, count in results]
        return result  # Returns list of categories sorted by popularity
    except Exception as e:
        logger.error(f"Error retrieving sorted categories by popularity: {e}")
        raise
def get_sorted_shops_by_popularity():
    """Retrieve shops sorted by popularity (number of transactions)"""
    try:
        session = db.get_session()
        stmt = select(
            Transaction.shop,
            func.count(Transaction.id).label('transaction_count')
        ).group_by(
            Transaction.shop
        ).order_by(
            func.count(Transaction.id).desc()
        )
        
        results = session.execute(stmt).all()
        logger.debug(f"Sorted shops by popularity: {results}")
        results = [shop for shop, count in results if shop is not None]
        return results  # Returns list of tuples: [(shop, count), ...]
    except Exception as e:
        logger.error(f"Error retrieving sorted shops by popularity: {e}")
        raise

def get_spendings(start_date: datetime, end_date: datetime):
    """Retrieve spendings for a given account and date range"""
    try:
        session = db.get_session()
        start_of_day = start_date
        end_of_day = end_date
        
        stmt = select(Transaction).where(Transaction.date.between(start_of_day, end_of_day))
        transactions = session.execute(stmt).scalars().all()
        return transactions
    except Exception as e:
        logger.error(f"Error retrieving spendings between {start_date} and {end_date}: {e}")
        raise
        
        
    except Exception as e:
        logger.error(f"Error retrieving spendings on {date}: {e}")
        raise

def get_grouped_spendings_by_category_for_current_month():
    """Retrieve spendings grouped by category for the current month"""
    try:
        session = db.get_session()
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        if now.month == 12:
            end_of_month = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_of_month = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
        
        stmt = select(
            Transaction.category,
            func.sum(Transaction.amount).label('total_amount'),
        ).where(
            Transaction.date.between(start_of_month, end_of_month)
        ).group_by(
            Transaction.category
        ).order_by(
            func.sum(Transaction.amount).desc()
        )
        
        results = session.execute(stmt).all()
        result_dict = {category: total for category, total in results}
        return result_dict  # Returns a dictionary: {category: total, ...}
    except Exception as e:
        logger.error(f"Error retrieving grouped spendings by category for current month: {e}")
        raise