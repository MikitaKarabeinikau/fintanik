from sqlalchemy import select, update, delete
from database import db
from database.models import Budget
from sqlalchemy.orm import Session
from datetime import datetime

def create_category_budget( user_telegram_id: int, category: str, amount: float, period_start: datetime, period_end: datetime) -> Budget:
    session = db.get_session()
    new_budget = Budget(
        user_id=user_telegram_id,
        category=category,
        amount=amount,
        period_start=period_start,
        period_end=period_end
    )
    session.add(new_budget)
    session.commit()
    session.refresh(new_budget)
    return new_budget

def create_catgory_budget_for_current_month(user_telegram_id: int, category: str, amount: float) -> Budget:
    now = datetime.now()
    period_start = datetime(now.year, now.month, 1)
    if now.month == 12:
        period_end = datetime(now.year + 1, 1, 1)
    else:
        period_end = datetime(now.year, now.month + 1, 1)
    
    return create_category_budget(user_telegram_id, category, amount, period_start, period_end)

def create_category_budget_for_next_month(user_telegram_id: int, category: str, amount: float) -> Budget:
    now = datetime.now()
    if now.month == 12:
        period_start = datetime(now.year + 1, 1, 1)
        period_end = datetime(now.year + 1, 2, 1)
    else:
        period_start = datetime(now.year, now.month + 1, 1)
        if now.month + 1 == 12:
            period_end = datetime(now.year + 1, 1, 1)
        else:
            period_end = datetime(now.year, now.month + 2, 1)
    
    return create_category_budget(user_telegram_id, category, amount, period_start, period_end)

def update_category_budget(budget_id: int, new_amount: float) -> Budget:
    session = db.get_session()
    budget = session.query(Budget).filter(Budget.id == budget_id).first()
    if budget:
        budget.amount = new_amount
        db.commit()
        db.refresh(budget)
    return budget

def get_all_budgets_for_current_month():
    session = db.get_session()
    now = datetime.now()
    period_start = datetime(now.year, now.month, 1)
    if now.month == 12:
        period_end = datetime(now.year + 1, 1, 1)
    else:
        period_end = datetime(now.year, now.month + 1, 1)
    stmt = select(Budget.category, Budget.amount).where(
        Budget.period_start == period_start,
        Budget.period_end == period_end
    )
    budgets = session.execute(stmt).all()
    budgets_dict = {category: amount for category, amount in budgets}
    return budgets_dict



def delete_category_budget( budget_id: int) -> bool:
    session = db.get_session()
    budget = session.query(Budget).filter(Budget.id == budget_id).first()
    if budget:
        db.delete(budget)
        db.commit()
        return True
    return False