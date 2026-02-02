from utils.config import Settings
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
import re
from keyboards.tutor import earnings_keyboard
logger = Settings.LOGGER
emoji = Settings.emoji


async def start_set_terms_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from database.terms.crud import get_unset_terms
    unset_terms = get_unset_terms()
    logger.info(f"Unset terms retrieved: {unset_terms}")
    if len(unset_terms) == 0:
        await update.message.reply_text("All terms are already set. if you want to update them, please use the update option.")
        return ConversationHandler.END
    
    context.user_data['terms'] = {}  # Initialize here!
    logger.info("Starting set terms flow.")
    
    keyboard = [
        [KeyboardButton(weekday.weekday)] for weekday in unset_terms
    ]
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    
    await update.message.reply_text(
        '📅 Please select the weekday for the new term:',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    
    return Settings.WAITING_FOR_WEEKDAY

async def handle_terms_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'SET TERMS BOUNDARIES':
        return await start_set_terms_flow(update, context)
    await update.message.reply_text("Terms Management selected. Here you can manage your tutoring terms.")
    return

async def handle_weekday_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    weekday = update.message.text
    if weekday == f"{emoji('BACK')} BACK":
        # Go back to terms menu
        await update.message.reply_text("Returning to Terms Management menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['terms'], resize_keyboard=True))
        return ConversationHandler.END
    context.user_data['terms']['weekday'] = weekday
    await update.message.reply_text(f"Selected weekday: {weekday}. Please enter the start time (HH:MM):", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(f"{emoji('BACK')} BACK")]], resize_keyboard=True))
    return Settings.WAITING_FOR_START_TIME

async def handle_start_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = update.message.text
    if start_time == f"{emoji('BACK')} BACK":
        # Go back to weekday selection
        from database.terms.crud import get_unset_terms
        unset_terms = get_unset_terms()
        keyboard = [
            [KeyboardButton(weekday.weekday)] for weekday in unset_terms
        ]
        keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
        await update.message.reply_text(
            '📅 Please select the weekday for the new term:',
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return Settings.WAITING_FOR_WEEKDAY
    if not re.match(r'^\d{2}:\d{2}$', start_time):
        await update.message.reply_text("❌ Invalid time format. Please enter the start time in HH:MM format:")
        return Settings.WAITING_FOR_START_TIME
    if start_time < "08:00" or start_time > "20:00":
        await update.message.reply_text("❌ Start time must be between 08:00 and 20:00. Please enter a valid start time (HH:MM):")
        return Settings.WAITING_FOR_START_TIME
    context.user_data['terms']['start_time'] = start_time
    await update.message.reply_text(f"Selected start time: {start_time}. Please enter the end time (HH:MM):", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(f"{emoji('BACK')} BACK")]], resize_keyboard=True))
    return Settings.WAITING_FOR_END_TIME

async def handle_end_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    end_time = update.message.text
    if end_time == f"{emoji('BACK')} BACK":
        # Go back to start time selection
        await update.message.reply_text("Please enter the start time (HH:MM):", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(f"{emoji('BACK')} BACK")]], resize_keyboard=True))
        return Settings.WAITING_FOR_START_TIME
    if not re.match(r'^\d{2}:\d{2}$', end_time):
        await update.message.reply_text("❌ Invalid time format. Please enter the end time in HH:MM format:")
        return Settings.WAITING_FOR_END_TIME
    if end_time < "08:00" or end_time > "21:00":
        await update.message.reply_text("❌ End time must be between 08:00 and 21:00. Please enter a valid end time (HH:MM):")
        return Settings.WAITING_FOR_END_TIME
    if end_time <= context.user_data['terms']['start_time']:
        await update.message.reply_text("❌ End time must be after start time. Please enter a valid end time (HH:MM):")
        return Settings.WAITING_FOR_END_TIME
    context.user_data['terms']['end_time'] = end_time
    terms = context.user_data.get('terms', {})
    weekday = terms.get('weekday')
    start_time = terms.get('start_time')
    logger.info(f"Received term details: {terms}")
    await update.message.reply_text(f"Term set for {weekday} from {start_time} to {end_time}.")
    from database.terms.crud import update_term
    try:
        update_term(weekday, start_time, end_time)
        await update.message.reply_text("✅ Term successfully created!")
    except Exception as e:
        logger.error(f"Error creating term: {e}")
        await update.message.reply_text("❌ Failed to create term. Please try again.")
    context.user_data.pop('terms', None)
    await update.message.reply_text("Returning to Terms Management menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['terms'], resize_keyboard=True))
    return ConversationHandler.END