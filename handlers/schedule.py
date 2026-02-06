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
    elif text == 'UPDATE LESSONS TIME':
        context.user_data['in_updating_schedule_lessons_menu'] = True
        schedule_lessons_keyboard = []
        from database.schedule.crud import get_schedules_by_student
        student_id = context.user_data.get('selected_student')[0]
        schedules = get_schedules_by_student(student_id)
        logger.info(f"Found {len(schedules)} schedules for student_id={student_id}")
        if not schedules:
            await update.message.reply_text("No lessons found to update.", 
                reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
            return
        for schedule in schedules:
            schedule_lessons_keyboard.append([KeyboardButton(f"{schedule.id} {schedule.weekday} at {schedule.time}")])
        schedule_lessons_keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
        await update.message.reply_text(
            "Please select the lesson to update:",
            reply_markup=ReplyKeyboardMarkup(schedule_lessons_keyboard, resize_keyboard=True)
        )
        return
    elif text == 'DELETE LESSON':
        from database.schedule.crud import get_schedules_by_student
        student_id = context.user_data.get('selected_student')[0]
        logger.info(f"DELETE LESSON clicked for student_id={student_id}")
        
        schedules = get_schedules_by_student(student_id)
        logger.info(f"Found {len(schedules)} schedules: {schedules}")
        
        if not schedules:
            await update.message.reply_text("No lessons found to delete.", 
                reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
            return
        
        # Set flag to track we're waiting for selection
        context.user_data['waiting_for_delete_schedule'] = True
        logger.info(f"Set waiting_for_delete_schedule flag")
        
        keyboard = [[KeyboardButton(f"{schedule.id} {schedule.weekday} at {schedule.time}")] for schedule in schedules]
        keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
        
        logger.info(f"Created keyboard with {len(keyboard)} buttons")
        
        await update.message.reply_text(
            "Please select the lesson to delete:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        logger.info("Sent message with keyboard")
        return
    elif text == f"{emoji('BACK')} BACK":
        # Go back to tutor menu
        context.user_data.pop('in_schedule_menu', None)
        context.user_data.pop('selected_student', None)
        context.user_data['in_earnings_menu'] = True
        keyboard = earnings_keyboard['tutor']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("💰 Earnings Menu:", reply_markup=reply_markup)
        return
    
    await update.message.reply_text("Schedule Management selected. Here you can manage your tutoring schedule.")

async def handle_schedule_lesson_to_delete_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    schedule_lesson = update.message.text
    
    if schedule_lesson == f"{emoji('BACK')} BACK":
        # Clear flag and return to schedule menu
        context.user_data.pop('waiting_for_delete_schedule', None)
        await update.message.reply_text("Cancelled deletion.", 
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
        return
    
    schedule_id = int(schedule_lesson.split()[0])
    from database.schedule.crud import delete_schedule
    
    try:
        delete_schedule(schedule_id)
        logger.info(f"Deleted schedule with ID {schedule_id}")
        await update.message.reply_text(f"✅ Lesson with ID {schedule_id} has been deleted.",
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
    except Exception as e:
        logger.error(f"Error deleting schedule with ID {schedule_id}: {e}")
        await update.message.reply_text(f"❌ Failed to delete lesson with ID {schedule_id}.",
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
    
    # Clear the flag
    context.user_data.pop('waiting_for_delete_schedule', None)

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
    student_id = context.user_data.get('selected_student').split()[0]
    schedule = create_schedule(student_id=student_id, weekday=lesson_data['day'], time=lesson_data['time'])
    create_lessons_from_schedule(schedule_id=schedule.id, weekday=lesson_data['day'], time_str=lesson_data['time'])
    await update.message.reply_text(
        f"✅ Lesson scheduled on {lesson_data['day']} at {lesson_data['time']}.",
        reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True)
    )
    
    # Clear lesson data
    context.user_data.pop('lesson', None)
    
    return ConversationHandler.END

async def handle_schedule_view_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    period = update.message.text

    if period == f"{emoji('BACK')} BACK":
        # Go back to tutor menu
        context.user_data.pop('in_schedule_view_menu', None)
        
        context.user_data['in_earnings_menu'] = True
        keyboard = earnings_keyboard['tutor']
        return_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("💰 Earnings Menu:", reply_markup=return_markup)
    else:
        # Map button text to period values
        period_map = {
            'TODAY': 'today',
            'THIS WEEK': 'week',
            'NEXT WEEK': 'next_week',
            'THIS MONTH': 'month',
            'NEXT MONTH': 'next_month'  
        }
        
        period_key = period_map.get(period, period.lower())
        
        from database.lessons.service import get_lessons_with_student_info
        lessons = get_lessons_with_student_info(period_key)
        if not lessons:
            await update.message.reply_text(f"No lessons found for the period: {period}.",
                reply_markup=ReplyKeyboardMarkup(earnings_keyboard['schedule_period'], resize_keyboard=True))
            return
        lessons_keyboard = [[KeyboardButton(f" {lesson[0].id} {lesson[1].id} {lesson[1].name} - {lesson[0].date.strftime('%Y-%m-%d %H:%M')}")] for lesson in lessons]
        lessons_keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
        await update.message.reply_text(
            f"📅 Lessons for the period: {period}",
            reply_markup=ReplyKeyboardMarkup(lessons_keyboard, resize_keyboard=True)
        )
        context.user_data.pop('in_schedule_view_menu', None)
        context.user_data['in_schedule_lessons_menu'] = True
        return

async def handle_lessons_schedule_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data['selected_student_id'] = text.split()[1]  # Store student id 
    context.user_data['selected_lesson'] = text
    if text == f"{emoji('BACK')} BACK":
        # Go back to schedule view menu
        context.user_data.pop('in_lessons_schedule_menu', None)
        context.user_data['in_schedule_view_menu'] = True
        keyboard = earnings_keyboard['schedule_period']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🗓️ Schedule Management selected. Here you can manage your tutoring schedule.", reply_markup=reply_markup)
        return
    
    keyboard = earnings_keyboard['lesson']
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"Lesson Details selected.\n{text}", reply_markup=reply_markup)
    context.user_data.pop('in_schedule_lessons_menu', None)
    context.user_data['in_lesson_details_menu'] = True
    return

async def handle_lesson_details_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == f"{emoji('BACK')} BACK":
        # Go back to lessons list
        context.user_data.pop('in_lesson_details_menu', None)
        context.user_data['in_schedule_lessons_menu'] = True
        selected_period = context.user_data.get('selected_period', 'TODAY')
        from database.lessons.service import get_lessons_with_student_info
        
        lessons = get_lessons_with_student_info(selected_period.lower())
        logger.info(f"Retrieved {len(lessons)} lessons for period '{selected_period}'")
        logger.info(f"Lessons: {lessons}")
        lessons_keyboard = [[KeyboardButton(f" {lesson[0].id} {lesson[1].name} - {lesson[0].date.strftime('%Y-%m-%d %H:%M')}")] for lesson in lessons]
        lessons_keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
        await update.message.reply_text(
            f"📅 Lessons for the period: {selected_period}",
            reply_markup=ReplyKeyboardMarkup(lessons_keyboard, resize_keyboard=True)
        )
        return
    elif text == 'COMPLETED':
        #TODO: Mark lesson as completed in DB. Write the logic here.  
        from database.lessons.service import complited_lesson
        selected_lesson_text = context.user_data.get('selected_lesson', '')
        logger.info(f"Marking lesson as completed: {selected_lesson_text}")
        lesson_id = int(selected_lesson_text.split()[0])
        complited_lesson(lesson_id)
        from database.students.services import get_student_balance_info
        response = get_student_balance_info(context.user_data.get('selected_student_id'))
        await update.message.reply_text(f"{response}",
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['tutor'], resize_keyboard=True))
        context.user_data.pop('in_lesson_details_menu', None)
        context.user_data['in_earnings_menu'] = True
        context.user_data.pop('selected_lesson', None)
        context.user_data.pop('selected_student_id', None)
        return
    elif text == 'CHANGE TERM':
        #TODO: Implement changing term logic here
        context.user_data['in_change_existed_lesson_term_menu'] = True
        await update.message.reply_text("Do you want nearest free terms in next 2 weeks or set a new term manually?",
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['change_lesson_term'], resize_keyboard=True))
        context.user_data.pop('in_lesson_details_menu', None)
        return
    elif text == 'CANCEL LESSON':
        #TODO: Implement cancel lesson logic here
        from database.lessons.crud import delete_lesson
        selected_lesson_text = context.user_data.get('selected_lesson', '')
        logger.info(f"Cancelling lesson: {selected_lesson_text}")
        lesson_id = int(selected_lesson_text.split()[0])
        delete_lesson(lesson_id)

        await update.message.reply_text(f"Lesson {lesson_id} for {selected_lesson_text.split()[2]} at {selected_lesson_text.split()[4]} has been cancelled.",
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['tutor'], resize_keyboard=True))
        context.user_data.pop('in_lesson_details_menu', None)
        context.user_data['in_earnings_menu'] = True
        return
    # Here you would handle other lesson detail actions like marking as paid/completed
    await update.message.reply_text("Feature not implemented yet.", 
        reply_markup=ReplyKeyboardMarkup(earnings_keyboard['lesson'], resize_keyboard=True))
    return

# ======================================================
# UPDATING SCHEDULE LESSONS MENU HANDLER
# ======================================================
async def handle_updating_schedule_lessons_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == f"{emoji('BACK')} BACK":
        # Go back to student schedule menu
        context.user_data.pop('in_updating_schedule_lessons_menu', None)
        context.user_data.pop('selected_lesson_id', None)
        await update.message.reply_text("Returning to Student Schedule menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
        return
    selected_lesson_id = update.message.text.split()[0]

    free_terms = get_free_terms(update.message.text.split()[1])  # Extract day from button text
    free_terms_keyboard = [[KeyboardButton(slot) for slot in row] for row in free_terms]
    free_terms_keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    context.user_data['selected_lesson_id'] = selected_lesson_id
    await update.message.reply_text(
        f"Selected lesson ID: {selected_lesson_id}. Please select the new time for the lesson:",
        reply_markup=ReplyKeyboardMarkup(free_terms_keyboard, resize_keyboard=True)
    )
    context.user_data.pop('in_updating_schedule_lessons_menu', None)
    context.user_data['in_updating_schedule_time_selection'] = True
    return

async def handle_updating_schedule_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Handling schedule time selection with text: {update.message.text}")
    selected_time = update.message.text
    if selected_time == f"{emoji('BACK')} BACK":
        # Go back to lessons list
        context.user_data.pop('in_updating_schedule_time_selection', None)
        await update.message.reply_text("Returning to lessons list.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
        return
    from database.schedule.crud import update_schedule_time
    try:
        update_schedule_time(schedule_id=context.user_data['selected_lesson_id'], new_time=selected_time)
        logger.info(f"Updated schedule ID {context.user_data['selected_lesson_id']} to new time {selected_time}")
        context.user_data.pop('in_updating_schedule_time_selection', None)
        await update.message.reply_text(f"✅ Lesson time updated to {selected_time}.",
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
    except Exception as e:
        logger.error(f"Error updating schedule ID {context.user_data['selected_lesson_id']} to new time {selected_time}: {e}")
        await update.message.reply_text(f"❌ Failed to update lesson time.",
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['student_schedule_menu'], resize_keyboard=True))
        context.user_data.pop('in_updating_schedule_time_selection', None)
        context.user_data.pop('selected_lesson_id', None)

    return

async def handle_change_existed_lesson_term_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == f"{emoji('BACK')} BACK":
        # Go back to lesson details menu
        context.user_data.pop('in_change_existed_lesson_term_menu', None)
        context.user_data['in_lesson_details_menu'] = True
        keyboard = earnings_keyboard['lesson']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Returning to Lesson Details menu.", reply_markup=reply_markup)
        return
    
    elif text == 'FREE TERMS':
        terms = get_free_terms_for_next_two_weeks()
        keyboard = []
        if terms[0] != []:
            for term in terms[0]:
                keyboard.append([KeyboardButton(term)])
        if terms[1] != []:
            for term in terms[1]:
                keyboard.append([KeyboardButton(term)])
        keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
        context.user_data.pop('in_change_existed_lesson_term_menu', None)
        context.user_data['free_term_update_selecting'] = True
        await update.message.reply_text(f"Please select a free term from the options below:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return
    
    elif text == 'SET NEW TERM':
        return
    handle_change_existed_lesson_term_menu


async def handle_free_term_update_selecting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_date_str = update.message.text
    if new_date_str == f"{emoji('BACK')} BACK":
        # Go back to change existed lesson term menu
        context.user_data.pop('free_term_update_selecting', None)
        context.user_data['in_change_existed_lesson_term_menu'] = True
        keyboard = earnings_keyboard['change_lesson_term']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Returning to Change Lesson Term menu.", reply_markup=reply_markup)
        return
    from database.lessons.crud import get_lesson, update_lesson
    lesson = get_lesson(int(context.user_data.get('selected_lesson').split()[0]))
    date_time = new_date_str.split()[1] + ' ' + new_date_str.split()[2]
    new_date = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
    lesson.date = new_date
    try:
        update_lesson(lesson)
        logger.info(f"Updated lesson ID {lesson.id} to new date {new_date}")
        context.user_data.pop('free_term_update_selecting', None)
        await update.message.reply_text(f"✅ Lesson date updated to {new_date}.",
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['tutor'], resize_keyboard=True))
        context.user_data.pop('selected_lesson', None)
    except Exception as e:
        logger.error(f"Error updating lesson ID {lesson.id} to new date {new_date}: {e}")
        await update.message.reply_text(f"❌ Failed to update lesson date.",
            reply_markup=ReplyKeyboardMarkup(earnings_keyboard['tutor'], resize_keyboard=True))
        context.user_data.pop('free_term_update_selecting', None)
        context.user_data.pop('selected_lesson', None)
    return

def get_free_terms_for_next_two_weeks():
    """
    Get all free time slots for the next two weeks, separated into weekdays and weekends.
    Considers:
    1. Existing lessons (to avoid double-booking)
    2. Work hour boundaries for each day
    3. Student can't have two lessons in one day
    
    Weekend = Days with 00:00-00:00 boundaries (flexible/special days)
    Weekdays = Days with actual work hour boundaries
    
    Returns:
        tuple: (weekday_terms, weekend_terms) where each is a list of strings
               Format: "Weekday YYYY-MM-DD HH:MM"
    """
    from database.lessons.crud import get_all_lessons_by_day
    from database.models import Terms
    from database import db
    from datetime import time as time_obj
    
    weekday_terms = []
    weekend_terms = []
    today = datetime.now()
    lesson_duration = timedelta(hours=1)
    session = db.get_session()
    
    # Define default weekend availability (since boundaries are 00:00-00:00)
    default_weekend_hours = (time_obj(12, 0, 0), time_obj(19, 0, 0))  # 12:00-19:00
    
    logger.info(f"Starting free terms search for next 14 days from {today.date()}")
    
    for day_offset in range(14):
        current_day = today + timedelta(days=day_offset)
        weekday_str = current_day.strftime('%A')
        
        # Query term for this weekday
        term = session.query(Terms).filter_by(weekday=weekday_str).first()
        if not term:
            continue
        
        # Check if student already has a lesson this day
        existing_lessons = get_all_lessons_by_day(current_day)
        if len(existing_lessons) > 0:
            logger.info(f"Student already has lesson(s) on {current_day.date()}, skipping")
            continue
        
        # Determine if this is weekend (00:00-00:00 boundaries)
        is_weekend = (term.start_time == time_obj(0, 0, 0) and term.end_time == time_obj(0, 0, 0))
        
        if is_weekend:
            # Use default weekend hours for flexibility
            work_hours = default_weekend_hours
            logger.info(f"{weekday_str} ({current_day.date()}) is weekend day, using {work_hours[0]}-{work_hours[1]}")
        else:
            # Use actual work hours from boundaries
            work_hours = (term.start_time, term.end_time)
            logger.info(f"{weekday_str} ({current_day.date()}) is weekday, using {work_hours[0]}-{work_hours[1]}")
        
        # Generate time slots
        start_time = datetime.combine(current_day.date(), work_hours[0])
        end_time = datetime.combine(current_day.date(), work_hours[1])
        
        current_time = start_time
        day_slots = []
        
        while current_time + lesson_duration <= end_time + lesson_duration:
            lesson_end = current_time + lesson_duration
            
            if lesson_end > end_time + lesson_duration:
                break
            
            # Format: "Weekday YYYY-MM-DD HH:MM"
            formatted_slot = f"{weekday_str} {current_time.strftime('%Y-%m-%d %H:%M')}"
            day_slots.append(formatted_slot)
            
            current_time += timedelta(minutes=30)
        
        # Add to appropriate array
        if is_weekend:
            weekend_terms.extend(day_slots)
            logger.info(f"Added {len(day_slots)} weekend slots for {weekday_str}")
        else:
            weekday_terms.extend(day_slots)
            logger.info(f"Added {len(day_slots)} weekday slots for {weekday_str}")
    
    logger.info(f"Total: {len(weekday_terms)} weekday terms, {len(weekend_terms)} weekend terms")
    return (weekday_terms, weekend_terms)
    