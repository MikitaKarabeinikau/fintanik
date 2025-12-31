from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from utils.decorators import is_authenticated
from utils.config import Settings

emoji = Settings.emoji

# TODO: v2.0.0 GET dynamic account list from DB and default list from config
def get_main_menu():
    """Create main menu keyboard with buttons"""

    keyboard = [
        [KeyboardButton('SPENDINGS')],
        [KeyboardButton(f'{emoji("SETTINGS")} SETTINGS')],
        [KeyboardButton(f"{emoji('LOGOUT')} Logout")],
        
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# TODO: v2.0.0 Write abstract handler for different main menu buttons
@is_authenticated
async def handle_main_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu button clicks"""
    text = update.message.text


    # Check if text starts with MONEY emoji or if we're in spendings/account context
    if text.startswith(f"{emoji('MONEY')}") or text == f"{emoji('NEW')} Add New Account" or text == f"{emoji('BACK')} BACK":
        from menus.spendings_menu import handle_spendings_menu
        return await handle_spendings_menu(update, context)


    elif text == 'SPENDINGS':
        from menus.spendings_menu import handle_spendings_menu
        return await handle_spendings_menu(update, context)
    
    elif text == "⚙️ Settings":
        from commands.settings import settings_command
        return await settings_command(update, context)
    
    elif text == f'HELP':
        from commands.help import help_command
        return await help_command(update, context)

    elif text == f"{emoji('LOGOUT')} Logout":
        from commands.logout import logout_command
        return await logout_command(update, context)
    
    else:
        await update.message.reply_text(
            "Please use the menu buttons below.",
            reply_markup=get_main_menu()
        )