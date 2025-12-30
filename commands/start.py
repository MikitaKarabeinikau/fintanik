import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from database.models import User
from utils.config import Settings

# Conversation state
WAITING_FOR_PASSWORD = 1
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Check if already authenticated
    if context.user_data.get('authenticated', False):
        await update.message.reply_text(
            Settings.greet(user.first_name)
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🔒 Welcome! Please enter the password to access the bot:"
    )
    return WAITING_FOR_PASSWORD