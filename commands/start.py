import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from database.models import User
from menus.main_menu import get_main_menu
from utils.config import Settings



# Conversation state
WAITING_FOR_PASSWORD = 1
logger = Settings.LOGGER


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user

    from database.user.crud import get_all_users
    existed_users = get_all_users()
    if user.id in [u.telegram_id for u in existed_users]:
            logger.info(f"User {user.id} already authenticated.")
            context.user_data['authenticated'] = True  
            await update.message.reply_text(
                "You are already authenticated. Use /help to see available commands.",
                reply_markup=get_main_menu()
            )
            return ConversationHandler.END
    else:
        logger.info(f"New user {user.id} started authentication.")
        await update.message.reply_text(
            "Welcome! Please enter the password to authenticate:"
        )
        return WAITING_FOR_PASSWORD

    
   