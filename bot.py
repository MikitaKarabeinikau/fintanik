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
from dotenv import load_dotenv
from database import db, User

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_PASSWORD = 1

# Get password from environment
BOT_PASSWORD = os.getenv('BOT_PASSWORD', 'default_password')


def get_main_menu():
    """Create main menu keyboard"""
    keyboard = [
        [KeyboardButton("📊 Show Spends"), KeyboardButton("Add Spend")],
        [KeyboardButton("💬 Load Check"), KeyboardButton("🚪 Logout")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


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


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Check if already authenticated
    if context.user_data.get('authenticated', False):
        await update.message.reply_text(
            f"👋 Welcome back {user.first_name}!\n\n"
            "You are already authenticated. Use the menu below or /help to see available commands.",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🔒 Welcome! Please enter the password to access the bot:"
    )
    return WAITING_FOR_PASSWORD


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if the provided password is correct"""
    user = update.effective_user
    password = update.message.text
    
    if password == BOT_PASSWORD:
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
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                session.add(db_user)
                session.commit()
                logger.info(f"New user registered: {user.id}")
                
                await update.message.reply_text(
                    f"✅ Authentication successful!\n\n"
                    f"👋 Welcome {user.first_name}! I'm your Telegram bot.\n\n"
                    "Use the menu below or type commands:",
                    reply_markup=get_main_menu()
                )
            else:
                await update.message.reply_text(
                    f"✅ Authentication successful!\n\n"
                    f"👋 Welcome back {user.first_name}!\n\n"
                    "Use the menu below or type commands:",
                    reply_markup=get_main_menu()
                )
        except Exception as e:
            logger.error(f"Error in check_password: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try /start again.")
        finally:
            session.close()
        
        return ConversationHandler.END
    else:
        # Wrong password
        await update.message.reply_text(
            "❌ Incorrect password. Please try again or use /cancel to exit."
        )
        return WAITING_FOR_PASSWORD


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the authentication process"""
    await update.message.reply_text(
        "❌ Authentication cancelled. Use /start to try again."
    )
    return ConversationHandler.END


async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logout command"""
    context.user_data['authenticated'] = False
    from telegram import ReplyKeyboardRemove
    await update.message.reply_text(
        "👋 You have been logged out. Use /start to log in again.",
        reply_markup=ReplyKeyboardRemove()
    )


@is_authenticated
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 *Available Commands:*

/help - Show this help message
/logout - Log out from the bot

📱 *Menu Buttons:*
• ❓ Help - Show this help
• 🚪 Logout - Log out from the bot

    """
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_main_menu())


@is_authenticated
async def spends_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    user = update.effective_user
    session = db.get_session()
    
    try:
        # Get user stats
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        
        if db_user:
            stats_text = f"""
📊 *Your Statistics:*

👤 Username: @{user.username or 'N/A'}
📅 Registered: {db_user.created_at.strftime('%Y-%m-%d %H:%M')}
            """
            await update.message.reply_text(stats_text, parse_mode='Markdown', reply_markup=get_main_menu())
        else:
            await update.message.reply_text("Please use /start first!", reply_markup=get_main_menu())
    except Exception as e:
        logger.error(f"Error in stats_command: {e}")
        await update.message.reply_text("Sorry, couldn't retrieve your statistics.", reply_markup=get_main_menu())
    finally:
        session.close()


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


async def post_init(application: Application):
    """Set bot commands for the menu"""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help message"),
        BotCommand("stats", "View your statistics"),
        BotCommand("logout", "Log out from the bot"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    """Start the bot"""
    # Get bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Check if password is set
    if BOT_PASSWORD == 'default_password':
        logger.warning("BOT_PASSWORD not set in environment variables! Using default password.")
    
    # Initialize database
    try:
        db.init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return
    
    # Create application
    application = Application.builder().token(token).post_init(post_init).build()
    
    # Create conversation handler for authentication
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            WAITING_FOR_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("spends", spends_menu))
    application.add_handler(CommandHandler("logout", logout_command))
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()