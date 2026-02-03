from utils.config import Settings
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
from database.lessons.service import create_lessons_from_schedule

from keyboards.tutor import earnings_keyboard
logger = Settings.LOGGER
emoji = Settings.emoji

async def handle_schedule_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'ADD LESSON IN SCHEDULE':
        return await start_add_lesson_in_schedule_flow(update, context)
    elif text == f"{emoji('BACK')} BACK":
        # Go back to tutor menu
        context.user_data.pop('in_schedule_menu', None)
        context.user_data['in_earnings_menu'] = True
        keyboard = earnings_keyboard['tutor']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("💰 Earnings Menu:", reply_markup=reply_markup)
        return
    else:
        await update.message.reply_text("Schedule Management selected. Here you can manage your tutoring schedule.")

def get_free_terms(day: str):
    """
    Generate free time slots for scheduling lessons.
    
    Args:
        day: Weekday (e.g., 'MONDAY', 'TUESDAY', etc.)
    
    Returns:
        list: List of keyboard buttons with available time slots
    """
    from database.schedule.crud import get_all_schedules_for_weekday
    from database.terms.crud import get_terms_boundaries
    
    # Get existing schedules and work hours
    existed_schedules = get_all_schedules_for_weekday(day)
    weekday_work_hours = get_terms_boundaries(day)  # Returns (time, time) objects
    
    # Extract scheduled times
    scheduled_times = [schedule.time for schedule in existed_schedules]
    
    # Convert time objects to datetime for easier manipulation
    today = datetime.now().date()
    start_time = datetime.combine(today, weekday_work_hours[0])
    end_time = datetime.combine(today, weekday_work_hours[1])
    
    # Generate all possible 30-minute slots
    free_slots = []
    current_time = start_time
    lesson_duration = timedelta(hours=1)
    
    while current_time <= end_time:
        # Check if lesson fits within work hours (lesson ends before or at end_time + 1 hour)
        lesson_end = current_time + lesson_duration
        if lesson_end > end_time + lesson_duration:
            break
        
        current_time_str = current_time.strftime("%H:%M")
        
        # Check if this slot is free (no conflict with existing lessons)
        is_free = True
        for scheduled_time in scheduled_times:
            scheduled_start = datetime.combine(today, datetime.strptime(scheduled_time, "%H:%M").time())
            scheduled_end = scheduled_start + lesson_duration
            
            # Check for overlap
            if not (lesson_end <= scheduled_start or current_time >= scheduled_end):
                is_free = False
                break
        
        if is_free:
            free_slots.append(current_time_str)
        
        # Move to next 30-minute slot
        current_time += timedelta(minutes=30)
    
    # Format as keyboard buttons
    # Check if we have both HH:00 and HH:30 times
    has_hour = any(slot.endswith(':00') for slot in free_slots)
    has_half = any(slot.endswith(':30') for slot in free_slots)
    
    if has_hour and has_half:
        # Two columns: HH:00 in left column, HH:30 in right column
        keyboard = []
        hour_slots = [slot for slot in free_slots if slot.endswith(':00')]
        half_slots = [slot for slot in free_slots if slot.endswith(':30')]
        
        max_len = max(len(hour_slots), len(half_slots))
        for i in range(max_len):
            row = []
            if i < len(hour_slots):
                row.append(hour_slots[i])
            if i < len(half_slots):
                row.append(half_slots[i])
            keyboard.append(row)
        
        return keyboard
    else:
        # Single column
        return free_slots

async def start_add_lesson_in_schedule_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lesson'] = {}  # Initialize lesson data
    logger.info("Starting add lesson in schedule flow.")
    from database.terms.crud import get_work_days
    work_days = get_work_days()
    keyboard = [
        [KeyboardButton(day)] for day in work_days
    ]
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    
    await update.message.reply_text(
        '📅 Please select the day for the new lesson:',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    
    return Settings.WAITING_FOR_LESSON_SCHEDULE_DAY

async def handle_lesson_schedule_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = update.message.text
    if day == f"{emoji('BACK')} BACK":
        # Go back to student schedule menu
        await update.message.reply_text("Returning to Student Schedule menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
        return ConversationHandler.END
    context.user_data['lesson']['day'] = day
    free_terms = get_free_terms(day)
    
    # Build keyboard from free_terms
    if free_terms and isinstance(free_terms[0], list):
        # Already formatted as rows (two columns)
        keyboard = [[KeyboardButton(slot) for slot in row] for row in free_terms]
    else:
        # Single column format
        keyboard = [[KeyboardButton(slot)] for slot in free_terms]
    
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    
    await update.message.reply_text(
        f"Selected day: {day}. Please select the time for the lesson:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return Settings.WAITING_FOR_LESSON_SCHEDULE_TIME

async def handle_schedule_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = update.message.text
    if time == f"{emoji('BACK')} BACK":
        # Go back to day selection
        keyboard = [
            [KeyboardButton(day)] for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        ]
        keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
        
        await update.message.reply_text(
            '📅 Please select the day for the new lesson:',
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return Settings.WAITING_FOR_LESSON_SCHEDULE_DAY
    
    context.user_data['lesson']['time'] = time
    
    # Here you would typically save the lesson to the database
    from database.schedule.crud import create_schedule
    lesson_data = context.user_data['lesson']
    student_id = context.user_data.get('selected_student')[0]
    schedule = create_schedule(student_id=student_id, weekday=lesson_data['day'], time=lesson_data['time'])
    create_lessons_from_schedule(schedule_id=schedule.id, weekday=lesson_data['day'], time_str=lesson_data['time'])
    await update.message.reply_text(
        f"✅ Lesson scheduled on {lesson_data['day']} at {lesson_data['time']}.",
        reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True)
    )
    
    # Clear lesson data
    context.user_data.pop('lesson', None)
    
    return ConversationHandler.END