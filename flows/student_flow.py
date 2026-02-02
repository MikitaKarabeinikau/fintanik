from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.config import Settings

WAITING_FOR_STUDENT_NAME = 1
WAITING_FOR_STUDENT_SURNAME = 2
WAITING_FOR_STUDENT_PRICE = 3
WAITING_FOR_PAYMENT_FREQUENCY = 4

emoji = Settings.emoji
logger = Settings.LOGGER

student_actions ={
    "name": {
        "stage": WAITING_FOR_STUDENT_NAME,
        "prev": None,
        "next": "surname",
        "prompt": "Enter the student's name:",
    },
    "surname": {
        "stage": WAITING_FOR_STUDENT_SURNAME,
        "prev": "name",
        "next": "price",
        "prompt": "Enter the student's surname:",
    },
    "price": {
        "stage": WAITING_FOR_STUDENT_PRICE,
        "prev": "surname",
        "next": "payment_frequency",
        "prompt": "Enter the student's price:",
    },
    "payment_frequency": {
        "stage": WAITING_FOR_PAYMENT_FREQUENCY,
        "prev": "price",
        "next": None,
        "prompt": "Enter the payment frequency (e.g., monthly, weekly):",
    }
}



async def student_flow(update: Update, context: ContextTypes.DEFAULT_TYPE, action_key: str):
    logger.info(f"Student flow action: {action_key}")
    if action_key in student_actions:
        if action_key == 'payment_frequency':
            from keyboards.tutor import earnings_keyboard
            keyboard = earnings_keyboard['payment_frequency']
            await update.message.reply_text("Please select the payment frequency:", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
        else:
            from keyboards.tutor import earnings_keyboard
            keyboard = earnings_keyboard['default_back_cancel']
            await update.message.reply_text(f'{student_actions[action_key]["prompt"]}', 
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
        
        
        return student_actions[action_key]["stage"] 
       
    elif action_key is None:
        await update.message.reply_text(f'Student information collection complete!\n\n{student_add_info(context)}')
        context.user_data.pop('student', None)
        #TODO: Save student to database
        return ConversationHandler.END
    else:
        await update.message.reply_text("Unknown action. Please try again.")
        return ConversationHandler.END

async def start_student_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👥 Starting student information collection.")
    student = {
        "name": None,
        "surname": None,
        "price": None,
        "payment_frequency": None
    }
    context.user_data['student'] = student
    return await student_flow(update, context, action_key='name')
