from telegram.ext import ContextTypes, ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
import datetime

from utils.date_picker import DatePickerKeyboard
from utils.config import Settings

emoji = Settings.emoji
logger = Settings.LOGGER    

WAITING_FOR_PAYMENT_AMOUNT = 100
WAITING_FOR_PAYMENT_DATE = 101

async def handle_payment_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date picker callbacks for credit flow"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    date_field = context.user_data.get('date_field')  # 'start_date' or 'end_date'
    
    if data.startswith("year_"):
        # Year selected, show months
        year = data.split("_")[1]
        context.user_data[f'{date_field}_year'] = year
        keyboard = DatePickerKeyboard.get_month_keyboard(year)
        await query.edit_message_text(
            f"Year: {year}\nSelect month:",
            reply_markup=keyboard
        )
    
    elif data.startswith("month_"):
        # Month selected, show days
        parts = data.split("_")
        year = parts[1]
        month = parts[2]
        context.user_data[f'{date_field}_month'] = month
        keyboard = DatePickerKeyboard.get_day_keyboard(year, month)
        await query.edit_message_text(
            f"Year: {year}, Month: {month}\nSelect day:",
            reply_markup=keyboard
        )
    
    elif data.startswith("day_"):
        # Day selected, date is complete
        parts = data.split("_")
        year = parts[1]
        month = parts[2]
        day = parts[3]
        selected_date = f"{year}-{month}-{day}"
        
        # Store the date
        context.user_data['payment_details']['date'] = datetime.datetime.strptime(selected_date, "%Y-%m-%d")
        
        await query.edit_message_text(f"✅ Selected {date_field.replace('_', ' ')}: {selected_date}")
        
        from database.payment.crud import create_payment
        payment_details = context.user_data['payment_details']
        create_payment(
            student_id=payment_details['student_id'],
            amount=payment_details['amount'],
            payment_date=payment_details['date']
        )
        
        await query.edit_message_text(
            f"✅ Payment recorded!\n"
            f"Amount: {payment_details['amount']}\n"
            f"Date: {selected_date}"
        )
        
        # Clean up
        context.user_data.pop('payment_details', None)
        context.user_data.pop('date_field', None)
        
        return ConversationHandler.END
    
    elif data == "date_back_year":
        # Go back to year selection
        keyboard = DatePickerKeyboard.get_year_keyboard()
        await query.edit_message_text("Select year:", reply_markup=keyboard)
    
    elif data.startswith("date_back_month_"):
        # Go back to month selection
        year = data.split("_")[3]
        keyboard = DatePickerKeyboard.get_month_keyboard(year)
        await query.edit_message_text(
            f"Year: {year}\nSelect month:",
            reply_markup=keyboard
        )

        from database.payment.crud import create_payment
        payment_details = context.user_data['payment_details']
        create_payment(
            student_id=payment_details['student_id'],
            amount=payment_details['amount'],
            date=payment_details['date']
        )
        
        await query.edit_message_text(
            f"✅ Payment recorded!\n"
            f"Amount: {payment_details['amount']}\n"
            f"Date: {selected_date}"
        )
        
        # Clean up
        context.user_data.pop('payment_details', None)
        context.user_data.pop('date_field', None)
        
        return ConversationHandler.END
    
    return WAITING_FOR_PAYMENT_DATE


async def start_payment_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: Initialize payment collection"""
    # Initialize payment data
    context.user_data['payment_details'] = {
        'student_id': context.user_data['selected_student'].split()[0],
        'amount': None,
        'date': None
    }
    
    await update.message.reply_text("💰 Provide payment amount:", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(f"{emoji('BACK')} BACK")]], resize_keyboard=True))
    return WAITING_FOR_PAYMENT_AMOUNT


async def handle_payment_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Receive and validate payment amount"""
    amount = update.message.text
    if amount == f"{emoji('BACK')} BACK":
        # Go back to student menu
        context.user_data.pop('payment_details', None)
        from handlers.students import handle_personal_student_menu
        return await handle_personal_student_menu(update, context)
    # Validation
    if not amount.isdigit():
        await update.message.reply_text(
            "❌ Please enter a valid numeric amount:"
        )
        return WAITING_FOR_PAYMENT_AMOUNT
    
    # Store amount
    context.user_data['payment_details']['amount'] = float(amount)
    
    # Show date picker
    context.user_data['date_field'] = 'payment_date'
    keyboard = DatePickerKeyboard.get_year_keyboard()
    await update.message.reply_text(
        "📅 Select payment date:\nChoose year:",
        reply_markup=keyboard
    )
    
    return WAITING_FOR_PAYMENT_DATE