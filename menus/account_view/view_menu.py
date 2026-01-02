import datetime
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from database import db
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

def get_dates_menu():
    """Create dates menu keyboard with buttons"""
    today = datetime.date.today()
    keyboard = [
        [KeyboardButton("TODAY")],
        [KeyboardButton("THIS WEEK")],
        [KeyboardButton("LAST 7 DAYS")],
        [KeyboardButton("THIS MONTH")],
        [KeyboardButton("LAST MONTH")],
        [KeyboardButton("THIS YEAR")],
        [KeyboardButton("LAST YEAR")],
        [KeyboardButton(f"{emoji('BACK')} BACK")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


emoji = Settings.emoji
logger = Settings.LOGGER

async def handle_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date selection and show transactions"""
    from database import db
    from database.models import Account
    text = update.message.text

    if not text:
        await update.message.reply_text(
            "❌ Invalid date selection. Please choose a valid option from the menu.",
            reply_markup=get_dates_menu()
        )
        return
    
    


    # Handle BACK button
    if text == f"{emoji('BACK')} BACK":
        context.user_data.pop('viewing_stats', None)
        from menus.account_menu import get_account_menu
        account_name = context.user_data.get('current_account')
        await update.message.reply_text(
            "Back to account menu",
            reply_markup=get_account_menu(account_name)
        )
        return
    
    transactions = handle_date_selection_sync(update, context,text)

    # Display transactions
    if not transactions:
        message = f"📅 {text}\n\n✅ No transactions found for this period."
    else:
        total = sum(t.amount for t in transactions)
        message = f"📅 {text}\n\n"
        for t in transactions:
            date_str = t.date.strftime("%Y-%m-%d") if t.date else "N/A"
            shop_str = f" at {t.shop}" if t.shop else ""
            message += f"💰 {t.amount:.2f} - {t.name or 'Unnamed'} ({t.category}){shop_str} - {date_str}\n"
        message += f"\n📊 Total: {total:.2f}"
    
    await update.message.reply_text(message, reply_markup=get_dates_menu())

def handle_date_selection_sync(update: Update, context: ContextTypes.DEFAULT_TYPE,text: str):
    start, end = parse_date_range(context, update, text)
    print(f"Parsed date range: {start} to {end}")

    transactions = get_spendings(session=db.get_session(),
                                 account=context.user_data.get('current_account'),
                                 start_date=start, end_date=end)
    return transactions