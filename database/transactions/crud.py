from database.db import db
from database.models import Transaction
from sqlalchemy.orm import Session
import logging
from datetime import date, datetime, timedelta,time
from utils.config import Settings

logger = Settings.LOGGER


def create_transaction(session: Session, user_id: int, account_id: int, amount: int, category: str, shop: str = None,name:str = None,date: datetime = datetime.utcnow()) -> Transaction:
    """Create a new transaction record"""
    try:
        new_transaction = Transaction(
            account_id = account_id,
            user_id=user_id,
            amount=amount,
            name = name,
            category=category,
            shop=shop,
            date=date
        )
        session.add(new_transaction)
        session.commit()
        session.refresh(new_transaction)
        return new_transaction
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating transaction: {e}")
        raise

def get_transactions(session: Session):
    """Retrieve all transactions"""
    try:
        return session.query(Transaction).all()
    except Exception as e:
        logger.error(f"Error retrieving transactions: {e}")
        raise

def update_transaction(session: Session, transaction_id: int, new_transaction) -> Transaction:
    """Update a transaction by its ID"""
    try:
        transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise ValueError(f"Transaction with ID {transaction_id} not found.")
        
        # Update fields
        transaction.amount = new_transaction.get('amount', transaction.amount)
        transaction.name = new_transaction.get('name', transaction.name)
        transaction.category = new_transaction.get('category', transaction.category)
        transaction.shop = new_transaction.get('shop', transaction.shop)
        transaction.date = new_transaction.get('date', transaction.date)
        
        session.commit()
        session.refresh(transaction)
        return transaction
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating transaction ID {transaction_id}: {e}")
        raise


def delete_transaction(session: Session, transaction_id: int) -> bool:
    """Delete a transaction by its ID"""
    try:
        transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            session.delete(transaction)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting transaction ID {transaction_id}: {e}")
        raise