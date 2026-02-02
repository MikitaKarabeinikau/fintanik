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
    
class Credit(Base):
    __tablename__ = 'credits'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    category = Column(String(255), nullable=True, default="Credit")
    lender_name = Column(String(255), nullable=False)
    total_amount = Column(Float, nullable=False)  # Store in cents
    monthly_payment = Column(Float, nullable=False)  # Store in cents
    date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    last_payment_amount = Column(Float, nullable=False)  # Store in cents
    paid = Column(Boolean, default=False)
    
    user = relationship("User", backref="credits")
    
    def __repr__(self):
        return f"<Credit(user_id={self.user_id}, lender_name={self.lender_name}, total={self.total})>"
    
class CreditPayment(Base):
    __tablename__ = 'credit_payments'
    
    id = Column(Integer, primary_key=True)
    credit_id = Column(Integer, ForeignKey('credits.id'), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=False)  # Store in cents
    status = Column(Boolean, default=False)  # e.g., pending, paid
    
    credit = relationship("Credit", backref="payments")
    
    def __repr__(self):
        return f"<CreditPayment(credit_id={self.credit_id}, amount={self.amount})>"
    
# ==========================================================================================================
# EARNING MODELS
# ==========================================================================================================
class Students(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    lesson_price = Column(Float, nullable=False)
    payment_frequency = Column(String(50), nullable=False) # e.g., monthly, weekly, per lesson
    balance = Column(Float, default=0.0)


    schedule = relationship("Schedules", backref="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(name={self.name}, surname={self.surname}, balance={self.balance})>"
    
class Schedules(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    weekday = Column(String(20), nullable=False)  # e.g., Monday, Tuesday
    time = Column(String(10), nullable=False)     # e.g., 14:00
    
    lessons = relationship("Lessons", backref="schedule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Schedule(student_id={self.student_id}, weekday={self.weekday}, time={self.time})>"
    
class Lessons(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('schedules.id'), nullable=False)
    paid = Column(Boolean, default=False)
    complited = Column(Boolean, default=False)
    date = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<Lesson(schedule_id={self.schedule_id}, date={self.date}, paid={self.paid}, complited={self.complited})>"
    
class Payments(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    student = relationship("Students", backref="payments")

    def __repr__(self):
        return f"<Payment(student_id={self.student_id}, amount={self.amount}, date={self.date})>"