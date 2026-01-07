from decimal import Decimal
from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime, Boolean, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
   
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"



class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)  # Who added it
    name = Column(String(255), nullable=True)
    shop = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)  # Store in cents
    category = Column(String(255), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="transactions")
    
    def __repr__(self):
        return f"<Transaction(user_id={self.user_id}, amount={self.amount}, category={self.category})>"


class Budget(Base):
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    category = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)  # Store in cents
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    user = relationship("User", backref="budgets")
    
    def __repr__(self):
        return f"<Budget(user_id={self.user_id}, category={self.category}, amount={self.amount})>"