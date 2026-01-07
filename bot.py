from email.mime import application
import os
from commands.cancel import cancel_command
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from dotenv import load_dotenv
from commands.transaction import WAITING_FOR_AMOUNT, WAITING_FOR_AMOUNT_UPDATE, WAITING_FOR_CATEGORY, WAITING_FOR_CATEGORY_UPDATE, WAITING_FOR_DATE, WAITING_FOR_DATE_UPDATE, WAITING_FOR_NAME, WAITING_FOR_NAME_UPDATE, WAITING_FOR_SHOP_NAME, WAITING_FOR_SHOP_NAME_UPDATE, handle_updating_field, receive_amount, receive_category, receive_date, receive_name, receive_shop_name, start_transaction, update_amount, update_category, update_date, update_name, update_shop_name
from database import db
from database.models import User, Transaction
from utils.utils import parse_date_range
from menus.main_menu import handle_main_menu_button
from utils.decorators import is_authenticated
from commands.start import start_command
from commands.help import help_command
from commands.logout import logout_command
from utils.auth import check_password
from utils.config import Settings


# Load environment variables
load_dotenv()

emoji = Settings.emoji

# Conversation states
WAITING_FOR_PASSWORD = 1


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    Settings.LOGGER.error(f"Update {update} caused error {context.error}")


async def post_init(application: Application):
    """Set bot commands for the menu"""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("logout", "Logout from your account"),
    ]
    await application.bot.set_my_commands(commands)




def main():
    """Start the bot"""
    # Get bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        Settings.LOGGER.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Check if password is set
    if Settings.PASSWORD == 'default_password':
        Settings.LOGGER.warning("PASSWORD not set in environment variables! Using default password.")
    
    # Initialize database
    try:
        db.init_db()
    except Exception as e:
        Settings.LOGGER.error(f"Failed to initialize database: {e}")
        return
    
    # Create application
    application = Application.builder().token(token).post_init(post_init).build()
    
    # Create conversation handler for authentication
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            WAITING_FOR_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )

  
    transaction_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(f'^{emoji("NEW")} Add Transaction$'),start_transaction)
    ],
    states={
        WAITING_FOR_AMOUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)
        ],
        WAITING_FOR_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)
        ],
        WAITING_FOR_CATEGORY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_category)
        ],
        WAITING_FOR_SHOP_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_shop_name)
        ],
        WAITING_FOR_DATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date)
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
)
    
    update_transaction_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex('^(AMOUNT|NAME|CATEGORY|SHOP|DATE)$'), handle_updating_field)
    ],
    states={
        WAITING_FOR_AMOUNT_UPDATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, update_amount)
        ],
        WAITING_FOR_NAME_UPDATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, update_name)
        ],
        WAITING_FOR_CATEGORY_UPDATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, update_category)
        ],
        WAITING_FOR_SHOP_NAME_UPDATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, update_shop_name)
        ],
        WAITING_FOR_DATE_UPDATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, update_date)
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
)
    


    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('logout', logout_command))
    application.add_handler(update_transaction_conv)
    application.add_handler(transaction_conv)
    application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_main_menu_button
    )
)
    
    # Start bot
    Settings.LOGGER.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()