from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from keyboards.tutor import earnings_keyboard
from utils.config import Settings

emoji = Settings.emoji
logger = Settings.LOGGER


async def handle_earnings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'EARNINGS':
        keyboard = earnings_keyboard['earnings']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        context.user_data['in_earnings_menu'] = True
        await update.message.reply_text("💰 Earnings Menu:", reply_markup=reply_markup)
        return
    elif text == 'TUTOR':
        keyboard = earnings_keyboard['tutor']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(f"👨‍🏫 Tutor Options:\n "\
                                        f"HERE WILL BE WARNIGS", reply_markup=reply_markup)
        return
    elif text == 'STUDENTS':
        keyboard = earnings_keyboard['students']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"HERE WILL BE STUDENTS OVERVIEW",parse_mode='HTML', reply_markup=reply_markup)
        context.user_data.pop('in_earnings_menu', None) 
        context.user_data['in_students_menu'] = True
        return
    elif text == 'TERMS':
        from database.terms.crud import get_unset_terms
        from handlers.terms import get_boundaries_info_table
        logger.info(f"usnet terms: {get_unset_terms()}")
        if len(get_unset_terms()) > 0:
        
            keyboard = earnings_keyboard['terms']
        else:
            keyboard = earnings_keyboard['terms_with_boundaries']
            
        message = get_boundaries_info_table() + "\n\nDEVELOP WARNING MESSAGE HERE"
        await update.message.reply_text(message, parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        context.user_data.pop('in_earnings_menu', None)
        context.user_data['in_terms_menu'] = True
        return
        keyboard = earnings_keyboard['terms_with_boundaries']
    elif text == 'SCHEDULE':
        keyboard = earnings_keyboard['schedule_period']
        await update.message.reply_text("🗓️ Schedule Management selected. Here you can manage your tutoring schedule.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        context.user_data.pop('in_earnings_menu', None)
        context.user_data['in_schedule_view_menu'] = True
        return
    elif text == f"{emoji('BACK')} BACK":
        # Go back to main menu
        context.user_data.pop('in_earnings_menu', None)
        keyboard = [
            [KeyboardButton('SPENDINGS')],
            [KeyboardButton(f"BUDGETS")],
            [KeyboardButton(f'CREDITS')],
            [KeyboardButton(f'EARNINGS')],
            [KeyboardButton(f"{emoji('LOGOUT')} Logout")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🏠 Main Menu:", reply_markup=reply_markup)
        return
    else:
        await update.message.reply_text("Unknown option selected.")
        return
