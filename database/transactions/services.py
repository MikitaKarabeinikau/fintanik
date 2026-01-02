from sqlalchemy import select
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

# Get transactions by category
def get_transactions_by_category(session: Session, category: str):
    try:
        """Retrieve transactions filtered by category"""
        return session.query(Transaction).filter(
            Transaction.category == category
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving transactions by category '{category}': {e}")
        raise

def get_transactions_by_category_this_day(session: Session, category: str):
    """Retrieve transactions for the current day filtered by category"""
    try:
        from datetime import datetime, time
        now = datetime.now()
        start_of_day = datetime.combine(now.date(), time.min)
        
        return session.query(Transaction).filter(
            Transaction.category == category,
            Transaction.date >= start_of_day
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving today's transactions by category '{category}': {e}")
        raise

def get_transactions_by_category_this_week(session: Session, category: str):
    """Retrieve transactions for the current week filtered by category"""
    try:
        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())
        
        return session.query(Transaction).filter(
            Transaction.category == category,
            Transaction.date >= start_of_week
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving this week's transactions by category '{category}': {e}")
        raise

def get_transactions_by_category_this_month(session: Session, category: str):
    """Retrieve transactions for the current month filtered by category"""
    try:
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        return session.query(Transaction).filter(
            Transaction.category == category,
            Transaction.date >= start_of_month
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving this month's transactions by category '{category}': {e}")
        raise

def get_transactions_by_category_this_year(session: Session, category: str):
    """Retrieve transactions for the current year filtered by category"""
    try:
        now = datetime.now()
        start_of_year = datetime(now.year, 1, 1)
        
        return session.query(Transaction).filter(
            Transaction.category == category,
            Transaction.date >= start_of_year
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving this year's transactions by category '{category}': {e}")
        raise

# Get transactions by shop
def get_transactions_by_shop(session: Session, shop: str):
    """Retrieve transactions filtered by shop"""
    try:
        return session.query(Transaction).filter(
                Transaction.shop == shop
            ).all()
    except Exception as e:
        logger.error(f"Error retrieving transactions by shop '{shop}': {e}")
        raise

def get_transactions_by_shop_this_day(session: Session, shop: str):
    """Retrieve transactions for the current day filtered by shop"""
    try:
        now = datetime.now()
        start_of_day = datetime.combine(now.date(), time.min)
        
        return session.query(Transaction).filter(
            Transaction.shop == shop,
            Transaction.date >= start_of_day
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving today's transactions by shop '{shop}': {e}")
        raise

def get_transactions_by_shop_this_week(session: Session, shop: str):
    """Retrieve transactions for the current week filtered by shop"""
    try:
        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())
        
        return session.query(Transaction).filter(
            Transaction.shop == shop,
            Transaction.date >= start_of_week
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving this week's transactions by shop '{shop}': {e}")
        raise

def get_transactions_by_shop_this_month(session: Session, shop: str):
    """Retrieve transactions for the current month filtered by shop"""
    try:
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
    
        return session.query(Transaction).filter(
            Transaction.shop == shop,
            Transaction.date >= start_of_month
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving this month's transactions by shop '{shop}': {e}")
        raise

def get_transactions_by_shop_this_year(session: Session, shop: str):
    """Retrieve transactions for the current year filtered by shop"""
    try:
        now = datetime.now()
        start_of_year = datetime(now.year, 1, 1)
        
        return session.query(Transaction).filter(
            Transaction.shop == shop,
            Transaction.date >= start_of_year
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving this year's transactions by shop '{shop}': {e}")
        raise



