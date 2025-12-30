from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes


async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logout command"""
    context.user_data['authenticated'] = False
    await update.message.reply_text(
        "👋 You have been logged out. Use /start to log in again.",
        reply_markup=ReplyKeyboardRemove()
    )