
from sqlalchemy import update
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes
from database import db
from database.transactions.services import get_spendings, get_spendings_grouped
from utils.config import Settings
from utils.utils import parse_date_range, view_statistics_all, view_statistics_grouped

emoji = Settings.emoji
logger = Settings.LOGGER

groups_menu = [
    [KeyboardButton("ALL TRANSACTIONS")],
    [KeyboardButton("BY CATEGORY")],
    [KeyboardButton("BY SHOP")],
    [KeyboardButton(f"{emoji('BACK')} BACK")]
]

def get_groups_menu():
    """Create groups menu keyboard with buttons"""
    return ReplyKeyboardMarkup(groups_menu, resize_keyboard=True)

async def handle_groups_menu(context: ContextTypes.DEFAULT_TYPE, update: Update):
    """Handle groups menu button clicks"""
    text = update.message.text
    date = context.user_data.get('selected_date_range', None)
    if date is None:
        from menus.account_view.view_menu import get_dates_menu
        await update.message.reply_text(
            "❌ No date range selected. Please select a date range first.",
            reply_markup=get_dates_menu()
        )
        return
    if text == f"{emoji('BACK')} BACK":
        from menus.account_menu import get_account_menu
        account_name = context.user_data.get('current_account')
        context.user_data['viewing_groups'] = False
        context.user_data['viewing_stats'] = True
        await update.message.reply_text(
            "Back to account menu",
            reply_markup=get_account_menu(account_name)
        )
        return
    elif text == "ALL TRANSACTIONS":
        transactions = get_all_transactions(update, context, date)
        message = view_statistics_all(date, transactions)

        await update.message.reply_text(
            message,
            reply_markup=get_groups_menu()
        )

        return
    elif text == "BY CATEGORY":
        transactions = get_groupe_transactions(update, context, date, group_by='category')
        message = view_statistics_grouped(date, transactions, group_by='category')

        await update.message.reply_text(
            message,
            reply_markup=get_groups_menu()
        )
    elif text == "BY SHOP":
        transactions = get_groupe_transactions(update, context, date, group_by='shop')
        message = view_statistics_grouped(date, transactions, group_by='shop')

        await update.message.reply_text(
            message,
            reply_markup=get_groups_menu()
        )
        return
    else:
        await update.message.reply_text(
            "❌ Invalid selection. Please choose a valid option from the menu.",
            reply_markup=get_groups_menu()
        )
        return
    
def get_all_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE,text: str):
    start, end = parse_date_range(context, update, text)
    print(f"Parsed date range: {start} to {end}")

    transactions = get_spendings(session=db.get_session(),
                                account=context.user_data.get('current_account'),
                                start_date=start, end_date=end)
    return transactions

def get_groupe_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE,text: str, group_by: str):
    start, end = parse_date_range(context, update, text)
    print(f"Parsed date range: {start} to {end}")

    transactions = get_spendings_grouped(session=db.get_session(),
                                account=context.user_data.get('current_account'),
                                start_date=start, end_date=end,
                                group_by=group_by)
    return transactions