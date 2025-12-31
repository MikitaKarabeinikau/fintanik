from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from utils.decorators import is_authenticated
from utils.config import Settings
from menus.account_menu import get_account_menu, handle_account_menu
from database.accounts.crud import create_spending_account, get_user_spending_accounts

emoji = Settings.emoji
WAITING_FOR_NEW_ACCOUNT_NAME = 1

@is_authenticated
async def receive_new_account_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and create new spending account"""
    account_name = update.message.text.strip()
    user_id = update.effective_user.id
    
    if len(account_name) < 2:
        await update.message.reply_text(
            "❌ Name too short. Please enter a valid account name:"
        )
        return WAITING_FOR_NEW_ACCOUNT_NAME
    
    # Save to database
    create_spending_account(user_id, account_name)
    
    await update.message.reply_text(
        f"✅ Account '{account_name}' created!",
        reply_markup=get_spendings_menu(update,context)
    )
    
    return ConversationHandler.END

def get_spendings_menu(update: Update,context: ContextTypes.DEFAULT_TYPE):
    """Create main menu keyboard with buttons"""
    user_spending_accounts = get_user_spending_accounts(update.effective_user.id)  # TODO: implement this function to fetch from DB
    
    keyboard = []
    for account in user_spending_accounts:
        keyboard.append([KeyboardButton(f"{emoji('MONEY')} {account['name']}")])
    keyboard.append([KeyboardButton(f"{emoji('NEW')} Add New Account")])
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

@is_authenticated
async def handle_spendings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle spendings menu button clicks"""
    text = update.message.text
    
    # If user is in account context, route to account menu
    if context.user_data.get('current_account'):
        return await handle_account_menu(update, context, context.user_data['current_account'])
    
    if text.startswith(f"{emoji('MONEY')}"):
        account_name = text.replace(f"{emoji('MONEY')} ", "")
        # Store account in context
        context.user_data['current_account'] = account_name
        # Show account menu
        await update.message.reply_text(
            f"📊 Account: {account_name}",
            reply_markup=get_account_menu(account_name)
        )
        
    elif text == f"{emoji('NEW')} Add New Account":
        await update.message.reply_text(
            "Please enter the name of the new spending account:",
            reply_markup=get_spendings_menu(update,context)
        )
        return WAITING_FOR_NEW_ACCOUNT_NAME
    
    elif text == f"{emoji('BACK')} BACK":
        context.user_data.pop('current_account', None)
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