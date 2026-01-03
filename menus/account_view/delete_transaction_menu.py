

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes
from database import db
from database.transactions.crud import delete_transaction
from database.transactions.services import get_spendings
from utils.config import Settings
from menus.account_view.view_menu import get_dates_menu,dates_keyboard
from utils.utils import parse_date_range
from menus.account_menu import get_account_menu

emoji = Settings.emoji

def get_delete_menu():
    return ReplyKeyboardMarkup(dates_keyboard, resize_keyboard=True)

def get_delete_list_menu(update: Update,context: ContextTypes.DEFAULT_TYPE):
    delete_list_keyboard = []
    start, end = parse_date_range(update = update, context = context,text = context.user_data.get('selected_date_range'))
    transaction_list = get_spendings(account=context.user_data.get('current_account'), start_date=start, end_date=end,session=db.get_session())
    for row in transaction_list:
        button_text = f"{row.id}: {row.amount} on {row.date} at {row.shop} ({row.category})"
        delete_list_keyboard.append([KeyboardButton(button_text)])
    delete_list_keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    return ReplyKeyboardMarkup(delete_list_keyboard, resize_keyboard=True)


async def handle_delete_transaction_menu(update, context):
    text = update.message.text

    if not text:
        await update.message.reply_text(
            "❌ Invalid date selection. Please choose a valid option from the menu.",
            reply_markup=get_dates_menu()
        )
        return

    # Handle BACK button
    if text == f"{emoji('BACK')} BACK":
        context.user_data.pop('deleting_transaction', None)
        account_name = context.user_data.get('current_account')
        await update.message.reply_text(
            "Back to account menu",
            reply_markup=get_account_menu(account_name)
        )
        return
    elif text in ["TODAY", "THIS WEEK", "LAST 7 DAYS", "THIS MONTH", "LAST MONTH", "THIS YEAR", "LAST YEAR"]:
        context.user_data['selected_date_range'] = text
        context.user_data['delete_list_menu'] = True
        context.user_data['deleting_transaction'] = False
        await update.message.reply_text(
            f"How would you like to view your statistics?",
        reply_markup=get_delete_list_menu(update=update, context=context))

async def handle_transaction_to_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == f"{emoji('BACK')} BACK":
        context.user_data.pop('delete_list_menu', None)
        context.user_data.pop('deleting_transaction', None)
        account_name = context.user_data.get('current_account')
        await update.message.reply_text(
            "Back to account menu",
            reply_markup=get_account_menu(account_name)
        )
        return

    try:
        transaction_id = int(text.split(":")[0])
        # Here you would add the logic to delete the transaction from the database
        delete_transaction(db.get_session(),transaction_id)  # You need to implement this function
        await update.message.reply_text(
            f"Transaction {transaction_id} has been deleted.",
            reply_markup=get_account_menu(context.user_data.get('current_account'))
        )
        print(context.user_data)
        context.user_data.pop('deleting_transaction', None)
        context.user_data.pop('delete_list_menu', None)
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Invalid selection. Please choose a valid transaction from the list.",
            reply_markup=get_delete_list_menu(update=update, context=context)
        )