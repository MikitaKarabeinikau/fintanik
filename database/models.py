from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship (users can share accounts)
account_members = Table(
    'account_members',
    Base.metadata,
    Column('account_id', Integer, ForeignKey('accounts.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role', String(50), default='member'),  # 'owner' or 'member'
    Column('joined_at', DateTime, default=datetime.utcnow)
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    accounts = relationship('Account', secondary=account_members, back_populates='members')
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class Account(Base):
    """Shared account for multiple users"""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    account_type = Column(String(50), default='SPENDING')  # e.g., 'spending', 'savings'
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    members = relationship('User', secondary=account_members, back_populates='accounts')
    transactions = relationship('Transaction', back_populates='account')
    
    def __repr__(self):
        return f"<Account(id={self.id}, name={self.name})>"


class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)  # Who added it
    name = Column(String(255), nullable=True)
    shop = Column(String(255), nullable=True)
    amount = Column(Integer, nullable=False)  # Store in cents
    category = Column(String(255), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship('Account', back_populates='transactions')
    
    def __repr__(self):
        return f"<Transaction(user_id={self.user_id}, amount={self.amount}, category={self.category})>"


class Invitation(Base):
    """Invitations to join an account"""
    __tablename__ = 'invitations'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    invited_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    invite_code = Column(String(50), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Invitation(code={self.invite_code}, account_id={self.account_id})>"