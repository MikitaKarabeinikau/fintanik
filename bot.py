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

from flows.student_flow import start_student_flow
from dotenv import load_dotenv
from commands.transaction import WAITING_FOR_AMOUNT, WAITING_FOR_AMOUNT_UPDATE, WAITING_FOR_CATEGORY, WAITING_FOR_CATEGORY_UPDATE, WAITING_FOR_DATE, WAITING_FOR_DATE_UPDATE, WAITING_FOR_NAME, WAITING_FOR_NAME_UPDATE, WAITING_FOR_SHOP_NAME, WAITING_FOR_SHOP_NAME_UPDATE, handle_updating_field, receive_amount, receive_category, receive_date, receive_name, receive_shop_name, start_transaction, update_amount, update_category, update_date, update_name, update_shop_name
from database import db
from database.models import User, Transaction
from handlers.payments import handle_payment_amount, handle_payment_date, start_payment_flow
from handlers.payments import handle_payment_date
from handlers.students import  receive_payment_frequency, receive_student_name, receive_student_price, receive_student_surname, student_specific_actions
from flows.student_flow import WAITING_FOR_PAYMENT_FREQUENCY, WAITING_FOR_STUDENT_NAME, WAITING_FOR_STUDENT_PRICE, WAITING_FOR_STUDENT_SURNAME
from menus.credit_menu import (
    FETCH_CATEGORY, 
    FETCH_END_DATE, 
    FETCH_LAST_PAYMENT, 
    FETCH_LENDER_NAME, 
    FETCH_MONTHLY_PAYMENT, 
    FETCH_START_DATE, 
    FETCH_TOTAL_AMOUNT, 
    receive_category as receive_credit_category,
    receive_end_date, 
    receive_last_payment, 
    receive_lender_name, 
    receive_monthly_payment, 
    receive_start_date, 
    receive_total_amount, 
    start_credit_flow
)
from utils.utils import parse_date_range
from menus.main_menu import handle_main_menu_button
from utils.decorators import is_authenticated
from commands.start import start_command
from commands.help import help_command
from commands.logout import logout_command
from utils.auth import check_password
from utils.config import Settings
from menus.credit_menu import handle_credit_date_callback

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
    
    # Start scheduler after bot is initialized
    from utils.scheduler import setup_scheduler
    setup_scheduler(application)
    Settings.LOGGER.info("Scheduler initialized")



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

    credit_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(f'^{emoji("NEW")} Add Credit/Loan$'),start_credit_flow)],
        states={
            FETCH_TOTAL_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_total_amount)],
            FETCH_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_credit_category)],
            FETCH_LENDER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_lender_name)],
            FETCH_START_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_start_date),
                CallbackQueryHandler(handle_credit_date_callback, pattern="^(year_|month_|day_|date_)")
            ],
            FETCH_END_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_end_date),
                CallbackQueryHandler(handle_credit_date_callback, pattern="^(year_|month_|day_|date_)")
            ],
            FETCH_MONTHLY_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_monthly_payment)],
            FETCH_LAST_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_last_payment)],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
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
    student_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex('ADD STUDENT'), start_student_flow)
    ],
    states={
        # Define states and handlers for student flow here
        WAITING_FOR_STUDENT_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_student_name)
        ],
        WAITING_FOR_STUDENT_SURNAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_student_surname)
        ],
        WAITING_FOR_STUDENT_PRICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_student_price)
        ],        
        WAITING_FOR_PAYMENT_FREQUENCY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_payment_frequency)
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
    WAITING_FOR_PAYMENT_AMOUNT = 100
    WAITING_FOR_PAYMENT_DATE = 101

    payment_conv = ConversationHandler(
    entry_points=[
        # Entry point: when "ADD PAYMENT" is clicked
        MessageHandler(
            filters.Regex('^ADD PAYMENT$'), 
            start_payment_flow  # Initialize the flow
        )
    ],
    states={
        WAITING_FOR_PAYMENT_AMOUNT: [
            # Handle text input for amount
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                handle_payment_amount
            )
        ],
        WAITING_FOR_PAYMENT_DATE: [
            # Handle date picker button clicks
            CallbackQueryHandler(
                handle_payment_date, 
                pattern="^(year_|month_|day_|date_)"
            )
        ],
    },
    fallbacks=[
        CommandHandler('cancel', cancel_command)
    ],
)
    application.add_handler(payment_conv)
    


    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(student_conv)
    application.add_handler(credit_conv)
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