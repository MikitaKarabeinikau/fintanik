import datetime

from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from utils.config import Settings
from database.transactions.services import get_sorted_categories_by_popularity
from telegram.ext import ContextTypes

emoji = Settings.emoji
# Add helper function to get month selection keyboard
def get_month_selection_keyboard():
    """Create month selection keyboard for current and next month"""
    today = datetime.datetime.now()
    current_month = today.strftime("%B %Y")  # e.g., "March 2026"
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1).strftime("%B %Y")
    
    keyboard = [
        [KeyboardButton(current_month)],
        [KeyboardButton(next_month)],
        [KeyboardButton(f"{emoji('BACK')} BACK")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Add helper function to get day selection keyboard
def get_day_selection_keyboard(year, month):
    """Create day selection keyboard in grid layout (7 columns) from today back to day 1"""
    today = datetime.datetime.now()
    
    # If selected month is current month, show from today back to day 1
    if year == today.year and month == today.month:
        start_day = today.day
    # If selected month is next month, show days from beginning
    else:
        start_day = min(today.day, (datetime.datetime(year, month, 1) + datetime.timedelta(days=32)).replace(day=1).day - 1)
    
    # Create a list of days from start_day down to 1
    days = list(range(start_day, 0, -1))
    
    # Create grid keyboard (7 columns per row)
    keyboard = []
    row = []
    for day in days:
        row.append(KeyboardButton(str(day)))
        if len(row) == 7:
            keyboard.append(row)
            row = []
    
    # Add remaining days in the last row
    if row:
        keyboard.append(row)
    
    # Add BACK button at the end
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_categories_keyboard(context: ContextTypes.DEFAULT_TYPE):
    """Create categories keyboard"""
    default_categories = Settings.CATEGORIES
    sorted_categories = get_sorted_categories_by_popularity()
    print(f"DEBUG: Sorted categories = {sorted_categories}")
    categories = [cat for cat in sorted_categories]
    for cat in default_categories:
        if cat not in categories:
            categories.append(cat)
    keyboard = [[KeyboardButton(category)] for category in categories]
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

