from database.models import User
from telegram import Update
from utils.config import Settings
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from menus.main_menu import get_main_menu
import logging

logger = logging.getLogger(__name__)

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if the provided password is correct"""
    user = update.effective_user
    password = update.message.text
    
    logger.info(f"Password check for user {user.id}")
    
    if password == Settings.BOT_PASSWORD:
        logger.info(f"Correct password from user {user.id}")
        
        # Password is correct
        context.user_data['authenticated'] = True
        
        # Register user in database
        session = db.get_session()
        try:
            db_user = session.query(User).filter_by(telegram_id=user.id).first()
            
            if not db_user:
                # Create new user
                db_user = User(
                    telegram_id=user.id,
                    username=user.username or user.username or "User"
                )
                session.add(db_user)
                session.commit()
                logger.info(f"New user registered: {user.id}")
                
                welcome_text = (
                    f"{Settings.emoji('DONE')} Authentication successful!\n\n"
                    f"{Settings.emoji('WELCOME')} Welcome {user.username}!\n\n"
                    "You can now use the bot. Try /help to see commands."
                )
            else:
                welcome_text = (
                    f"{Settings.emoji('DONE')} Authentication successful!\n\n"
                    f"{Settings.emoji('WELCOME')} Welcome back {user.username}!\n\n"
                    "Use /help to see available commands."
                )
            
            # Send message BEFORE deleting password
            await update.message.reply_text(
                welcome_text,
                reply_markup=get_main_menu()
            )
            
            # Try to delete password message (optional, may fail)
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete password message: {e}")
            
        except Exception as e:
            logger.error(f"Error in check_password: {e}", exc_info=True)
            await update.message.reply_text(
                "Sorry, something went wrong. Please try /start again."
            )
        finally:
            session.close()
        
        return ConversationHandler.END
    else:
        # Wrong password
        logger.info(f"Incorrect password from user {user.id}")
        await update.message.reply_text(
            "❌ Incorrect password. Please try again or use /cancel to exit."
        )
        from commands.start import WAITING_FOR_PASSWORD
        return WAITING_FOR_PASSWORD