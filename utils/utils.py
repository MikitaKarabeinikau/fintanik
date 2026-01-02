from telegram import Update
from telegram.ext import ContextTypes
import datetime

def parse_date_range(context: ContextTypes.DEFAULT_TYPE, update: Update, text: str):
    """Parse date range from button text"""
    today = datetime.date.today()
    
    if text == "TODAY":
        start = datetime.datetime.combine(today, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)
        return start, end
    
    elif text == "THIS WEEK":
        start_of_week = today - datetime.timedelta(days=today.weekday())
        start = datetime.datetime.combine(start_of_week, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)
        return start, end
    
    elif text == "LAST 7 DAYS":
        last_7_days = today - datetime.timedelta(days=7)
        start = datetime.datetime.combine(last_7_days, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)
        return start, end
    
    elif text == "THIS MONTH":
        start_of_month = today.replace(day=1)
        start = datetime.datetime.combine(start_of_month, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)
        return start, end
    
    elif text == "LAST MONTH":
        first_of_this_month = today.replace(day=1)
        last_month_end = first_of_this_month - datetime.timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        start = datetime.datetime.combine(last_month_start, datetime.time.min)
        end = datetime.datetime.combine(last_month_end, datetime.time.max)
        return start, end
    
    elif text == "THIS YEAR":
        start_of_year = today.replace(month=1, day=1)
        start = datetime.datetime.combine(start_of_year, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)
        return start, end
    
    elif text == "LAST YEAR":
        start_of_last_year = today.replace(year=today.year - 1, month=1, day=1)
        end_of_last_year = today.replace(year=today.year - 1, month=12, day=31)
        start = datetime.datetime.combine(start_of_last_year, datetime.time.min)
        end = datetime.datetime.combine(end_of_last_year, datetime.time.max)
        return start, end
    
    else:
        return None, None