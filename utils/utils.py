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
        return f"📅 {period}\n\nNo transactions found."
    
    # Calculate total
    total = sum(t.amount for t in transactions)
    
    # Find max lengths for dynamic sizing
    max_name = max((len(t.name or "Unnamed") for t in transactions), default=10)
    max_name = min(max_name, 20)  # Cap at 20
    max_category = max((len(t.category or "N/A") for t in transactions), default=10)
    max_category = min(max_category, 15)  # Cap at 15
    
    # Header
    lines = [f"📅 {period}\n"]
    lines.append(f"{'Name':<{max_name}} {'Category':<{max_category}} {'Amount':>10}")
    lines.append("-" * (max_name + max_category + 10 + 4))
    
    # Transactions
    for t in transactions:
        name = (t.name or 'Unnamed')[:max_name]
        category = (t.category or "N/A")[:max_category]
        
        lines.append(f"{name:<{max_name}} {category:<{max_category}} {t.amount:>8.2f} zl")
    
    # Footer
    lines.append("-" * (max_name + max_category + 10 + 4))
    lines.append(f"{'TOTAL':<{max_name}} {'':<{max_category}} {total:>8.2f} zl")
    lines.append(f"\n📈 Total: {len(transactions)} transactions")
    
    return "\n".join(lines)

def view_statistics_grouped(period, grouped_data, group_by):
    """Format grouped statistics with aligned columns"""
    if not grouped_data:
        return f"📅 {period}\n\nNo transactions found."
    
    # Calculate totals
    total_amount = sum(row[1] for row in grouped_data)
    total_count = sum(row[2] for row in grouped_data)
    
    # Find max length for group names
    max_group = max((len(str(row[0] or "N/A")) for row in grouped_data), default=10)
    max_group = min(max_group, 20)  # Cap at 20
    
    # Header
    lines = [f"📅 {period}"]
    lines.append(f"📂 Grouped by: {group_by.upper()}\n")
    lines.append(f"{group_by.capitalize():<{max_group}} {'Amount':>12} {'Count':>8}")
    lines.append("-" * (max_group + 12 + 8 + 4))
    
    # Data rows
    for row in sorted(grouped_data, key=lambda x: x[1], reverse=True):
        group_name = (str(row[0] or "N/A"))[:max_group]
        amount = row[1]
        count = row[2]
        lines.append(f"{group_name:<{max_group}} {amount:>12.2f} {count:>8}")
    
    # Footer
    lines.append("-" * (max_group + 12 + 8 + 4))
    lines.append(f"{'TOTAL':<{max_group}} {total_amount:>12.2f} {total_count:>8}")
    
    return "\n".join(lines)