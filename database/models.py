from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"
    
class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey('users.telegram_id'), nullable=False, index=True)
    shop = Column(String(255), nullable=True, default=None)
    amount = Column(Integer, nullable=False)
    category = Column(String(255), nullable=False)
    date = Column(DateTime, default=datetime.timezone.utc.now)
    
    def __repr__(self):
        return f"<Transaction(user_id={self.user_id}, amount={self.amount}, category={self.category})>"