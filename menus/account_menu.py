from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from utils.decorators import is_authenticated
from utils.config import Settings

emoji = Settings.emoji

def get_account_menu(account_name: str):
    """Create account menu keyboard with buttons"""
    keyboard = [
        [KeyboardButton(f"{emoji('NEW')} Add Transaction")],
        [KeyboardButton(f"{emoji('UPDATE')} Update Transaction")],
        [KeyboardButton(f"{emoji('DELETE')} Delete Transaction")],
        [KeyboardButton(f'{emoji("INVITE")} Invite User')],
        [KeyboardButton(f"{emoji('STATS')} View Statistics")],
        [KeyboardButton(f"{emoji('BACK')} BACK")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

@is_authenticated
async def handle_account_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, account_name: str):
    """Handle account menu button clicks"""
    text = update.message.text

    if text == f"{emoji('NEW')} Add Transaction":
        await update.message.reply_text(
            f"You chose to add a transaction to '{account_name}'. (Functionality to be implemented)",
            reply_markup=get_account_menu(account_name)
        )
    
    elif text == f"{emoji('UPDATE')} Update Transaction":
        await update.message.reply_text(
            f"You chose to update a transaction in '{account_name}'. (Functionality to be implemented)",
            reply_markup=get_account_menu(account_name)
        )
    
    elif text == f"{emoji('DELETE')} Delete Transaction":
        await update.message.reply_text(
            f"You chose to delete a transaction from '{account_name}'. (Functionality to be implemented)",
            reply_markup=get_account_menu(account_name)
        )
    
    elif text == f'{emoji("INVITE")} Invite User':
        await update.message.reply_text(
            f"You chose to invite a user to '{account_name}'. (Functionality to be implemented)",
            reply_markup=get_account_menu(account_name)
        )
    
    elif text == f"{emoji('STATS')} View Statistics":
        await update.message.reply_text(
            f"You chose to view statistics for '{account_name}'. (Functionality to be implemented)",
            reply_markup=get_account_menu(account_name)
        )
    
    elif text == f"{emoji('BACK')} BACK":
        context.user_data.pop('current_account', None)
        from menus.spendings_menu import get_spendings_menu
        await update.message.reply_text(
            "Back to spendings",
            reply_markup=get_spendings_menu(update, context)
        )
    else:
        await update.message.reply_text(
            "Please use the menu buttons below.",
            reply_markup=get_account_menu(account_name)
        )