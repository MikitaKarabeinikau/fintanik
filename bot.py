from email.mime import application
import os
from commands.account_managment import WAITING_ACCOUNT_NAME, create_account, handle_invite_callback, handle_leave_callback, invite_user, join_account, leave_account, leave_account, list_accounts, receive_account_name
from commands.transaction import WAITING_FOR_CATEGORY, WAITING_FOR_DATE, WAITING_FOR_NAME, WAITING_FOR_SHOP_NAME, ask_for, receive_amount, receive_category, receive_date, receive_name, receive_shop_name, start_transaction, transaction_flow
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
from database import db
from database.models import User, Transaction
from menus.account_menu import WAITING_FOR_AMOUNT, handle_account_menu
from menus.main_menu import handle_main_menu_button
from utils.decorators import is_authenticated
from commands.start import start_command
from commands.help import help_command
from commands.logout import logout_command
from utils.auth import check_password
from utils.config import Settings
from menus.spendings_menu import (
    handle_spendings_menu, 
    receive_new_account_name, 
    WAITING_FOR_NEW_ACCOUNT_NAME
)


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

    spendings_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{emoji('NEW')} Add New Account$"), handle_spendings_menu)],
    states={
        WAITING_FOR_NEW_ACCOUNT_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_account_name)
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    )

    transaction_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(f'^{emoji("NEW")} Add Transaction$'), lambda u, c: start_transaction(u, c))
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

   
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('logout', logout_command))

    account_conv = ConversationHandler(
        entry_points=[CommandHandler('createaccount', create_account)],
        states={
            WAITING_ACCOUNT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_account_name)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
    )

    application.add_handler(account_conv)
    application.add_handler(spendings_conv)
    application.add_handler(transaction_conv)
    application.add_handler(CommandHandler('accounts', list_accounts))
    application.add_handler(CommandHandler('invite', invite_user))
    application.add_handler(CommandHandler('join', join_account))
    application.add_handler(CommandHandler('leave', leave_account))
    application.add_handler(CallbackQueryHandler(handle_invite_callback, pattern='^invite_account_'))
    application.add_handler(CallbackQueryHandler(handle_leave_callback, pattern='^leave_account_'))
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