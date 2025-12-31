from database.db import db
from database.models import Transaction
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta,time
from utils.config import Settings

logger = Settings.LOGGER


def create_transaction(session: Session, user_id: int, amount: int, category: str, shop: str = None) -> Transaction:
    """Create a new transaction record"""
    try:
        new_transaction = Transaction(
            user_id=user_id,
            amount=amount,
            category=category,
            shop=shop
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

def update_transaction(session: Session, transaction_id: int, **kwargs) -> Transaction:
    """Update a transaction by its ID"""
    try:
        transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            return None
        
        for key, value in kwargs.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        
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