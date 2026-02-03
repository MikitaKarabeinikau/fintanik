from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards.tutor import earnings_keyboard
from utils.config import Settings
emoji = Settings.emoji
from flows.student_flow import student_actions, student_flow

logger = Settings.LOGGER

def show_student_info(student_id: str):
    from database.schedule.crud import get_schedules_by_student
    from database.students.crud import get_student
    student = get_student(int(student_id))
    student_schedule = get_schedules_by_student(student.id)
    return f"Name: {student.name}\n" \
           f"Surname: {student.surname}\n" \
           f"Lesson Price: {student.lesson_price}\n" \
           f"Payment Frequency: {student.payment_frequency}\n" \
           f"Balance: {student.balance}\n" \
           f"Schedule: {student_schedule}\n"

async def handle_students_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'ADD STUDENT':
        await update.message.reply_text(f"👥 Add Student selected.\n{student_add_info(context=context)} Please provide student details.")
        return
    elif text == 'VIEW STUDENTS':
        context.user_data['viewing_students'] = True
        await update.message.reply_text("👥 View Students selected. Here is the list of your students.")
        from database.students.crud import get_all_students
        students = get_all_students()
        if not students:
            logger.info("No students found in the database.")
            await update.message.reply_text("No students found.")
            return ConversationHandler.END
        student_list = "\n".join([f"{student.id}. {student.name} {student.surname}" for student in students])
        keyboard = [] 
        for student in students:
            keyboard.append([f"{student.id} {student.name} {student.surname}"])
        keyboard.append([f"{emoji('BACK')} BACK"])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"Choose a student:", reply_markup=reply_markup)
        return
    elif text == f"{emoji('BACK')} BACK":
        # Go back to students menu
        context.user_data.pop('in_students_menu', None)
        context.user_data.pop('viewing_students', None)
        context.user_data['in_earnings_menu'] = True
        keyboard = earnings_keyboard['tutor']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("💰 Earnings Menu:", reply_markup=reply_markup)
        return
    else:
        # Handle clicking on a student name
        if context.user_data.get('viewing_students'):
            return await handle_specific_student(update, context)
        await update.message.reply_text("Unknown option selected.")
        return
    

async def receive_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_name = update.message.text
    if student_name == f'{emoji("CANCEL")} CANCEL' or student_name in [f'{emoji("BACK")} BACK']:
        from telegram import ReplyKeyboardMarkup
        keyboard = earnings_keyboard['students']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Student addition cancelled.", reply_markup=reply_markup)
        context.user_data.pop('student', None)
        return ConversationHandler.END
    context.user_data['student']['name'] = student_name
    await update.message.reply_text(f"{student_add_info(context=context)}\n Please enter the student's surname:")
    next = student_actions['name']['next']
    return await student_flow(update, context, action_key=next)

async def receive_student_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_surname = update.message.text
    if student_surname == f'{emoji("CANCEL")} CANCEL':
        await update.message.reply_text("Student addition cancelled.")
        context.user_data.pop('student', None)
        return ConversationHandler.END
    elif student_surname in [f'{emoji("BACK")} BACK']:
        await update.message.reply_text("Please enter the student's name again:")
        from flows.student_flow import WAITING_FOR_STUDENT_NAME
        return WAITING_FOR_STUDENT_NAME
    context.user_data['student']['surname'] = student_surname
    await update.message.reply_text(f"{student_add_info(context=context)}\n Please enter the student's price:")
    next = student_actions['surname']['next']
    return await student_flow(update, context, action_key=next)

async def receive_student_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_price = update.message.text
    if not student_price.isdigit():
        await update.message.reply_text("Please enter a valid numeric price for the student:")
        from flows.student_flow import WAITING_FOR_STUDENT_PRICE
        return WAITING_FOR_STUDENT_PRICE
    if student_price == f'{emoji("CANCEL")} CANCEL':
        await update.message.reply_text("Student addition cancelled.")
        context.user_data.pop('student', None)
        return ConversationHandler.END
    elif student_price in [f'{emoji("BACK")} BACK']:
        await update.message.reply_text("Please enter the student's surname again:")
        from flows.student_flow import WAITING_FOR_STUDENT_SURNAME
        return WAITING_FOR_STUDENT_SURNAME
    context.user_data['student']['price'] = student_price
    await update.message.reply_text(f"{student_add_info(context=context)}\n Please enter the payment frequency (e.g., monthly, weekly):")
    next = student_actions['price']['next']
    return await student_flow(update, context, action_key=next)

async def receive_payment_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment_frequency = update.message.text
    if payment_frequency == f'{emoji("CANCEL")} CANCEL':
        await update.message.reply_text("Student addition cancelled.")
        context.user_data.pop('student', None)
        return ConversationHandler.END  
    elif payment_frequency not in ['DAILY', 'WEEKLY', 'MONTHLY']:
        await update.message.reply_text("Please select a valid payment frequency from the keyboard options:")
        from flows.student_flow import WAITING_FOR_PAYMENT_FREQUENCY
        return WAITING_FOR_PAYMENT_FREQUENCY
    elif payment_frequency in [f'{emoji("BACK")} BACK']:
        await update.message.reply_text("Please enter the student's price again:")
        from flows.student_flow import WAITING_FOR_STUDENT_PRICE
        return WAITING_FOR_STUDENT_PRICE
    context.user_data['student']['payment_frequency'] = payment_frequency.lower()
    await update.message.reply_text(f"{student_add_info(context=context)}\n Student information collection complete!")
    
    from database.students.crud import create_student
    create_student(
        name=context.user_data['student']['name'],
        surname=context.user_data['student']['surname'],
        lesson_price=float(context.user_data['student']['price']),
        payment_frequency=context.user_data['student']['payment_frequency']
    )

    logger.info(f"Student created: {context.user_data['student']}")
    context.user_data.pop('student', None)
    keyboard = earnings_keyboard['students']
    await update.message.reply_text("👥 Students Management:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ConversationHandler.END


def student_add_info(context: ContextTypes.DEFAULT_TYPE):
    student = context.user_data.get("student", {})  # Use .get() with default empty dict
    return f'Name: {student.get("name", "")}\n' \
           f'Surname: {student.get("surname", "")}\n' \
           f'Price: {student.get("price", "")}\n' \
           f'Payment Frequency: {student.get("payment_frequency", "")}\n'


async def handle_specific_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    

    context.user_data.pop('viewing_students', None)
    context.user_data['selected_student'] = text
    keyboard = earnings_keyboard['personal_student_menu']
    await update.message.reply_text(f"Selected student: {show_student_info(context.user_data['selected_student'].split()[0])}", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return

async def student_specific_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'SCHEDULE':
        context.user_data['in_schedule_menu'] = True
        student_schedule_menu = earnings_keyboard['student_schedule_menu']
        keyboard = ReplyKeyboardMarkup(student_schedule_menu, resize_keyboard=True)
        await update.message.reply_text("👨‍🏫 Student Schedule Menu:", reply_markup=keyboard)
        return
    elif text == 'ADD PAYMENT':
        await update.message.reply_text("Provide payment amount:")
        from handlers.payments import start_payment_flow
        return start_payment_flow(update, context)
    elif text == 'UPDATE STUDENT INFO':
        await update.message.reply_text("Updating student information...")
        return
    elif text == 'DELETE STUDENT':
        id = context.user_data['selected_student'].split()[0]
        from database.students.crud import delete_student
        delete_student(student_id=int(id))
        await update.message.reply_text("Student deleted successfully.")
        context.user_data.pop('selected_student', None)
        keyboard = earnings_keyboard['students']
        await update.message.reply_text("👥 Students Management:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return
    elif text == f'{emoji("BACK")} BACK':
        keyboard = earnings_keyboard['students']
        await update.message.reply_text("👥 Students Management:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        context.user_data.pop('selected_student', None)
        return
    else:
        await update.message.reply_text("Unknown option selected.")
        return

