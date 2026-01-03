from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from menus.account_view.view_menu import get_dates_menu
from utils.decorators import is_authenticated
from utils.config import Settings
emoji = Settings.emoji

WAITING_FOR_AMOUNT =  1 


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

async def handle_account_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, account_name: str):
    """Handle account menu button clicks"""
    text = update.message.text
    from commands.transaction import transaction_actions, transaction_flow

    if text == f"{emoji('NEW')} Add Transaction":
        transaction = transaction_actions['transaction']
        flow = transaction_flow(update, context, action_key='amount',transaction=transaction)
        context.user_data['transaction'] = transaction
        return await flow
    
    elif text == f"{emoji('UPDATE')} Update Transaction":
        context.user_data['date_range_updating'] = True 
        await update.message.reply_text(
            f"You chose to update a transaction from '{account_name}'. Select a date range to view transactions:",
            reply_markup=get_dates_menu()
        )
    
    elif text == f"{emoji('DELETE')} Delete Transaction":
        context.user_data['deleting_transaction'] = True
        from menus.account_view.delete_transaction_menu import get_delete_menu
        await update.message.reply_text(
            f"You chose to delete a transaction from '{account_name}'. Select a date range to view transactions:",
            reply_markup=get_delete_menu()
        )
    
    elif text == f'{emoji("INVITE")} Invite User':
        await update.message.reply_text(
            f"You chose to invite a user to '{account_name}'. (Functionality to be implemented)",
            reply_markup=get_account_menu()
        )
    
    elif text == f"{emoji('STATS')} View Statistics":
        from menus.account_menu import view_menu
        account_name = context.user_data.get('current_account')
        context.user_data['viewing_stats'] = True
        await update.message.reply_text(
            f"{emoji('STATS')} View Statistics selected for account '{account_name}'."
        )
        return await get_dates_menu()
        
    
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