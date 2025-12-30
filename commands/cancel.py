
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the authentication process"""
    await update.message.reply_text(
        "❌ Authentication cancelled. Use /start to try again."
    )
    return ConversationHandler.END
