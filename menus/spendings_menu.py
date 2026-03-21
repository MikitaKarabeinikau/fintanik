from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from menus.account_view.view_menu import get_dates_menu
from utils.decorators import is_authenticated
from utils.config import Settings
from database.transactions.services import (get_spendings)
from utils.utils import parse_date_range

emoji = Settings.emoji

def get_updating_field_menu():
    updating_field_keyboard = [
        [KeyboardButton("AMOUNT")],
        [KeyboardButton("NAME")],
        [KeyboardButton("CATEGORY")],
        [KeyboardButton("SHOP")],
        [KeyboardButton("DATE")],
        [KeyboardButton("UPDATE TRANSACTION")],
        [KeyboardButton(f"{emoji('BACK')} BACK")]
    ]
    return ReplyKeyboardMarkup(updating_field_keyboard, resize_keyboard=True)

def get_update_list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update_list_keyboard = []
    start, end = parse_date_range(update=update, context=context, text=context.user_data.get('selected_date_range'))
    transaction_list = get_spendings(start_date=start, end_date=end)
    for row in transaction_list:
        # Format date as string without spaces
        date_str = row.date.strftime("%Y-%m-%d") if row.date else "N/A"
        # Use | as separator
        button_text = f"{row.id}|{row.name or 'Unnamed'}|{row.amount}|{row.shop or 'N/A'}|{row.category or 'N/A'}|{date_str}"
        update_list_keyboard.append([KeyboardButton(button_text)])
    update_list_keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    return ReplyKeyboardMarkup(update_list_keyboard, resize_keyboard=True)



def get_spendings_menu(update: Update,context: ContextTypes.DEFAULT_TYPE):
    """Create main menu keyboard with buttons"""
    
    keyboard = [
    [KeyboardButton(f"{emoji('NEW')} Add Transaction")],
    [KeyboardButton(f"{emoji('UPDATE')} Update Transaction")],
    [KeyboardButton(f"{emoji('DELETE')} Delete Transaction")],
    [KeyboardButton(f"{emoji('STATS')} View Statistics")],
    ]
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

@is_authenticated
async def handle_spendings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle spendings menu button clicks"""
    text = update.message.text
  
    if text == f"{emoji('NEW')} Add Transaction":
        from commands.transaction import transaction_flow, transaction_actions
        transaction = transaction_actions['transaction']
        flow = transaction_flow(update, context, action_key='amount',transaction=transaction)
        context.user_data['transaction'] = transaction
        return await flow
    
    elif text == f"{emoji('UPDATE')} Update Transaction":
        print(f"🔍 SPENDINGS_MENU: Matched UPDATE! Setting date_range_updating=True")
        context.user_data['date_range_updating'] = True 
        await update.message.reply_text(
            f"Select a date range to view transactions:",
            reply_markup=get_dates_menu()
        )
        print(f"🔍 SPENDINGS_MENU: Sent dates menu, returning now")
        return
    
    elif text == f"{emoji('DELETE')} Delete Transaction":
        context.user_data['deleting_transaction'] = True
        from menus.account_view.delete_transaction_menu import get_delete_menu
        await update.message.reply_text(
            f"Select a date range to view transactions:",
            reply_markup=get_delete_menu()
        )
        return
    elif text == f"{emoji('STATS')} View Statistics":
        context.user_data['viewing_stats'] = True
        await update.message.reply_text(
            f"{emoji('STATS')} View Statistics."
        )
        return
        
    elif text == f"{emoji('BACK')} BACK":
        from menus.main_menu import get_main_menu
        await update.message.reply_text(
            "Back to main menu",
            reply_markup=get_main_menu()
        )
    else:
        await update.message.reply_text(
            "Please use the menu buttons below.",
            reply_markup=get_spendings_menu(update,context)
        )