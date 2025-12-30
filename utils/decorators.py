import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

def is_authenticated(func):
    """Decorator to check if user is authenticated"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.user_data.get('authenticated', False):
            await update.message.reply_text(
                "🔒 Please authenticate first using /start"
            )
            return ConversationHandler.END
        return await func(update, context)
    return wrapper