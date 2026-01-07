import datetime
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from menus.account_view.groups_menu import get_groups_menu
from utils.decorators import is_authenticated
from database.transactions.services import get_spendings
from utils.config import Settings
emoji = Settings.emoji
from utils.utils import parse_date_range

ACCOUNT_VIEW_TODAY = 1
ACCOUNT_VIEW_THIS_WEEK = 2
ACCOUNT_VIEW_THIS_MONTH = 3
ACCOUNT_VIEW_LAST_MONTH = 4
ACCOUNT_VIEW_THIS_YEAR = 5
ACCOUNT_VIEW_LAST_YEAR = 6

dates_keyboard = [
        [KeyboardButton("TODAY")],
        [KeyboardButton("THIS WEEK")],
        [KeyboardButton("LAST 7 DAYS")],
        [KeyboardButton("THIS MONTH")],
        [KeyboardButton("LAST MONTH")],
        [KeyboardButton("THIS YEAR")],
        [KeyboardButton("LAST YEAR")],
        [KeyboardButton(f"{emoji('BACK')} BACK")]
    ]

def get_dates_menu():
    """Create dates menu keyboard with buttons"""
    return ReplyKeyboardMarkup(dates_keyboard, resize_keyboard=True)


emoji = Settings.emoji
logger = Settings.LOGGER

async def handle_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date selection and show transactions"""
    text = update.message.text

    if not text:
        await update.message.reply_text(
            "❌ Invalid date selection. Please choose a valid option from the menu.",
            reply_markup=get_dates_menu()
        )
        return
    
    
    # Handle BACK button
    if text == f"{emoji('BACK')} BACK":
        from menus.spendings_menu import get_spendings_menu
        context.user_data.pop('viewing_stats', None)
        context.user_data.pop('viewing_groups', None)
        context.user_data.pop('selected_date_range', None)
        await update.message.reply_text(
            "Back to account menu",
            reply_markup=get_spendings_menu(update, context)
        )
        return
    elif text in ["TODAY", "THIS WEEK", "LAST 7 DAYS", "THIS MONTH", "LAST MONTH", "THIS YEAR", "LAST YEAR"]:
        context.user_data['selected_date_range'] = text
        context.user_data['viewing_groups'] = True
        context.user_data['viewing_stats'] = False
        await update.message.reply_text(
            f"How would you like to view your statistics?",
        reply_markup=get_groups_menu())

