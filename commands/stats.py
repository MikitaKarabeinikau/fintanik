import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import db
from database.models import Transaction
from datetime import datetime, timedelta
from sqlalchemy import func

logger = logging.getLogger(__name__)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    user = update.effective_user
    session = db.get_session()
    
    try:
        
        await update.message.reply_text("IN PROGRESS", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in stats_command: {e}")
        await update.message.reply_text("Couldn't retrieve statistics.")
    finally:
        session.close()