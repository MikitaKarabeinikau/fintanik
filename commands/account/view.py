from telegram import Update
from telegram.ext import ContextTypes
from menus.account_view.view_menu import ACCOUNT_VIEW_LAST_MONTH, ACCOUNT_VIEW_LAST_MONTH, ACCOUNT_VIEW_LAST_YEAR, ACCOUNT_VIEW_THIS_MONTH, ACCOUNT_VIEW_THIS_MONTH, ACCOUNT_VIEW_THIS_MONTH, ACCOUNT_VIEW_THIS_WEEK, ACCOUNT_VIEW_LAST_YEAR, ACCOUNT_VIEW_THIS_YEAR, ACCOUNT_VIEW_TODAY, get_dates_menu
from utils.decorators import is_authenticated
from database.transactions.services import get_spendings
from utils.config import Settings

emoji = Settings.emoji


async def start_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start viewing transactions based on selected date range"""
    await update.message.reply_text(
        "Please select a date range to view transactions:",
        reply_markup=get_dates_menu()
    )


