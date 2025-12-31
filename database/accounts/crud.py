from sqlalchemy.orm import Session
from database.models import User, Account, account_members
from utils.config import Settings
from sqlalchemy.exc import SQLAlchemyError
from database import db

logger = Settings.LOGGER

def create_spending_account(user_telegram_id: int, account_name: str):
    """Create a new spending account and associate it with the user"""
    session: Session = db.get_session()
    try:
        # Fetch the user
        user = session.query(User).filter_by(telegram_id=user_telegram_id).first()
        if not user:
            logger.error(f"User with telegram_id {user_telegram_id} not found.")
            return None
        
        # Create new account
        new_account = Account(name=account_name, owner_id=user.id)
        session.add(new_account)
        session.commit()
        
        # Associate user with the new account as owner
        stmt = account_members.insert().values(
            account_id=new_account.id,
            user_id=user.id,
            role='owner'
        )
        session.execute(stmt)
        session.commit()
        
        logger.info(f"Created new spending account '{account_name}' for user {user_telegram_id}.")
        return new_account
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating spending account: {e}")
        return None
    finally:
        session.close()

def get_user_spending_accounts(user_telegram_id: int):
    """Retrieve all spending accounts associated with a user"""
    session: Session = db.get_session()
    try:
        user = session.query(User).filter_by(telegram_id=user_telegram_id).first()
        if not user:
            logger.error(f"User with telegram_id {user_telegram_id} not found.")
            return []
        
        accounts = (
            session.query(Account)
            .join(account_members, Account.id == account_members.c.account_id)
            .filter(account_members.c.user_id == user.id)
            .all()
        )
        
        account_list = [{'id': acc.id, 'name': acc.name} for acc in accounts]
        return account_list
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving user spending accounts: {e}")
        return []
    finally:
        session.close()