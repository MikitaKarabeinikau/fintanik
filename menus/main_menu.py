from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from utils.decorators import is_authenticated
from utils.config import Settings

emoji = Settings.emoji

def get_main_menu():
    """Create main menu keyboard with buttons"""
    keyboard = [
        [KeyboardButton(f"{emoji('MONEY')} Add Expense")],
        [KeyboardButton(f"{emoji('ACCOUNT')} Account")],
        [KeyboardButton(f"{emoji('STATS')} My Statistics")],
        
        [KeyboardButton(f"{emoji('LOGOUT')} Logout")],
        
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)



async def handle_main_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu button clicks"""
    text = update.message.text
    
    if text == " Add Expense":
        # Trigger add expense conversation
        from handlers.add_expense import start
        return await start(update, context)
    
    elif text == "📊 My Statistics":
        from commands.stats import stats_command
        return await stats_command(update, context)
    elif text == f"{emoji('ACCOUNT')} Account":
        from commands.account_managment import list_accounts
        return await list_accounts(update, context)
    
    # elif text == "📁 Categories":
    #     from commands.categories import categories_command
    #     return await categories_command(update, context)
    
    # elif text == "⚙️ Settings":
    #     from commands.settings import settings_command
    #     return await settings_command(update, context)
    
    elif text == "❓ Help":
        from commands.help import help_command
        return await help_command(update, context)
    
    else:
        await update.message.reply_text(
            "Please use the menu buttons below.",
            reply_markup=get_main_menu()
        )