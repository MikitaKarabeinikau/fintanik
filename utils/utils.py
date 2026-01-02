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
    
def view_statistics_all(period, transactions):
    """Format all transactions in a pretty aligned table"""
    if not transactions:
        return f"📅 {period}\n\n✅ No transactions found for this period."
    
    # Calculate total
    total = sum(t.amount for t in transactions)
    
    # Header
    message = f"📊 {'='*50}\n"
    message += f"📅 {period}\n"
    message += f"{'='*50}\n\n"
    
    # Table header with aligned columns
    message += f"{'Date':<12} {'Amount':>8} {'Category':<12} {'Name':<15} {'Shop':<12}\n"
    message += f"{'-'*50}\n"
    
    # Transactions - one line per transaction
    for t in transactions:
        date_str = t.date.strftime("%Y-%m-%d") if t.date else "N/A"
        name = (t.name or 'Unnamed')[:14]  # Truncate if too long
        category = (t.category or "N/A")[:11]
        shop = (t.shop or "-")[:11]
        
        message += f"{date_str:<12} {t.amount:>8.2f} {category:<12} {name:<15} {shop:<12}\n"
    
    # Footer
    message += f"{'-'*50}\n"
    message += f"{'TOTAL':<12} {total:>8.2f}\n"
    message += f"{'='*50}\n"
    message += f"📈 Transactions: {len(transactions)}\n"
    
    return message

def view_statistics_grouped(period, grouped_data, group_by):
    """Format grouped statistics with aligned columns"""
    if not grouped_data:
        return f"📅 {period}\n\n✅ No transactions found for this period."
    
    # Calculate totals
    total_amount = sum(row[1] for row in grouped_data)
    total_count = sum(row[2] for row in grouped_data)
    
    # Header
    message = f"📊 {'='*50}\n"
    message += f"📅 {period}\n"
    message += f"📂 Grouped by: {group_by.upper()}\n"
    message += f"{'='*50}\n\n"
    
    # Table header with aligned columns
    message += f"{group_by.capitalize():<25} {'Amount':>12} {'Count':>8}\n"
    message += f"{'-'*50}\n"
    
    # Data rows - values aligned to column headers
    for row in grouped_data:
        group_name = (row[0] or "N/A")[:24]  # Truncate if too long
        amount = row[1]
        count = row[2]
        message += f"{group_name:<25} {amount:>12.2f} {count:>8}\n"
    
    # Footer with aligned totals
    message += f"{'-'*50}\n"
    message += f"{'TOTAL':<25} {total_amount:>12.2f} {total_count:>8}\n"
    message += f"{'='*50}\n"
    
    return message