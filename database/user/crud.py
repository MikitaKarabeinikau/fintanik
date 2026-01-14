from database.models import User
from utils.config import Settings
from database import db

logger = Settings.LOGGER

def get_user_by_telegram_id(telegram_id: int):
    """Retrieve a user by their Telegram ID"""
    session = db.get_session()
    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        return user
    except Exception as e:
        logger.error(f"Error retrieving user with Telegram ID {telegram_id}: {e}")
        raise
    finally:
        session.close()

def get_all_users():
    """Get all users from database"""
    from database import db
    from database.models import User
    session = db.get_session()
    return session.query(User).all()