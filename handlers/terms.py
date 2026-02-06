from utils.config import Settings
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
import re
from keyboards.tutor import earnings_keyboard
logger = Settings.LOGGER
emoji = Settings.emoji


def get_boundaries_info_table():
    from database.terms.crud import get_all_terms
    boundaries = get_all_terms()
    
    if not boundaries:
        return "No term boundaries set."
    
    response = "<b>📅 Term Boundaries:</b>\n\n"
    
    for term in boundaries:
        start = str(term.start_time) if hasattr(term.start_time, 'strftime') else term.start_time
        end = str(term.end_time) if hasattr(term.end_time, 'strftime') else term.end_time
        
        if start == "00:00:00" and end == "00:00:00":
            schedule_str = "00:00 - 00:00"
            status = "🔴 Weekend"
        else:
            schedule_str = f"{start} - {end}"
            status = "✅ Working"
        
        response += f"<b>{term.weekday}:</b> {schedule_str}\n{status}\n\n"
    
    return response

def get_free_terms_table():
    from handlers.schedule import get_free_terms
    terms = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": [],
        "Sunday": []
    }
    for day in terms.keys():
        free_slots = get_free_terms(day)
        # Handle both keyboard format (2D list) and simple list format (1D list)
        for item in free_slots:
            if isinstance(item, list):
                # It's a row from keyboard layout
                for slot in item:
                    if slot != '00:00':
                        terms[day].append(slot)
            else:
                # It's a simple string
                if item != '00:00':
                    terms[day].append(item)
    response = "<b>📅 Free Terms:</b>\n\n"
    
    has_terms = False
    for day, slots in terms.items():
        if not slots:
            continue
        has_terms = True
        slots_str = ', '.join(slots)
        response += f"<b>{day}:</b>\n{slots_str}\n\n"
    
    if not has_terms:
        response += "No free terms available."
    
    return response
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
    from database.terms.crud import get_all_terms
    message = ""

    if text == 'SET TERMS BOUNDARIES':
        return await start_set_terms_flow(update, context)
    elif text == f'{emoji("BACK")} BACK':
        # Go back to earnings menu
        context.user_data.pop('in_terms_menu', None)
        context.user_data['in_earnings_menu'] = True
        keyboard = earnings_keyboard['earnings']
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("💰 Earnings Menu:", reply_markup=reply_markup)
        return
    elif text == 'FREE TERMS':
        response = get_free_terms_table() 
        await update.message.reply_text(response, parse_mode='HTML')
        return
    elif text == 'CHANGE TERMS BOUNDARIES':
        context.user_data.pop('in_terms_menu', None)
        context.user_data['in_change_terms_boundaries'] = True
        boundaries = get_all_terms()
        if boundaries:
            keyboard = [[KeyboardButton(f'{term.id} {term.weekday} {term.start_time} {term.end_time}')] for term in boundaries]
            keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
            await update.message.reply_text("Please select the term you want to change.",reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return
    else:
        message = get_boundaries_info_table() 
        await update.message.reply_text(message, parse_mode='HTML')
        return

async def handle_weekday_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    weekday = update.message.text
    if weekday == f"{emoji('BACK')} BACK":
        # Go back to terms menu
        await update.message.reply_text("Returning to Terms Management menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['terms'], resize_keyboard=True))
        return ConversationHandler.END
    context.user_data['terms']['weekday'] = weekday
    keyboard = [[KeyboardButton('WEEKEND')],[KeyboardButton(f"{emoji('BACK')} BACK")]]
    await update.message.reply_text(f"Selected weekday: {weekday}. Please enter the start time (HH:MM):", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
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
    elif start_time == "WEEKEND":
        #WEEKEND SPECIAL CASE
        context.user_data['terms']['start_time'] = '00:00'
        context.user_data['terms']['end_time'] = '00:00'
        from database.terms.crud import update_term
        try:
            weekday = context.user_data['terms']['weekday']
            start_time = context.user_data['terms']['start_time']
            end_time = context.user_data['terms']['end_time']
            update_term(weekday, start_time, end_time)
            await update.message.reply_text("✅ Term successfully created!")
        except Exception as e:
            logger.error(f"Error creating term: {e}")
            await update.message.reply_text("❌ Failed to create term. Please try again.")
            
        context.user_data.pop('terms', None)
        await update.message.reply_text("Returning to Terms Management menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['terms'], resize_keyboard=True))
        return ConversationHandler.END 
    else:
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

# =======================================
# Change Terms Boundaries Handler
# =======================================

async def handle_change_terms_boundaries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    term_id = update.message.text.split()[0]
    if term_id == f"{emoji('BACK')}":
        # Go back to terms menu
        await update.message.reply_text("Returning to Terms Management menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['terms'], resize_keyboard=True))
        context.user_data.pop('in_change_terms_boundaries', None)
        context.user_data['in_terms_menu'] = True
        return
    context.user_data['change_term_id'] = term_id
    keyboard = [[KeyboardButton('START')],[KeyboardButton('END')],[KeyboardButton('WEEKEND')],[KeyboardButton(f"{emoji('BACK')} BACK")]]
    await update.message.reply_text("Please select which boundary you want to change (START or END) or set as WEEKEND:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    context.user_data.pop('in_change_terms_boundaries', None)
    context.user_data['in_selecting_boundary'] = True
    return

async def handle_selecting_boundary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selection = update.message.text
    
    if selection == f"{emoji('BACK')} BACK":
        # Go back to terms menu
        await update.message.reply_text("Returning to Terms Management menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['terms'], resize_keyboard=True))
        context.user_data.pop('in_selecting_boundary', None)
        context.user_data.pop('in_change_terms_boundaries', None)
        context.user_data['in_terms_menu'] = True
        return
    elif selection == 'WEEKEND':
        # User wants to set this day as weekend
        from database.terms.crud import get_all_terms
        from database.schedule.crud import get_all_schedules_for_weekday
        
        term_id = int(context.user_data['change_term_id'])
        all_terms = get_all_terms()
        current_term = next((t for t in all_terms if t.id == term_id), None)
        
        if not current_term:
            await update.message.reply_text("❌ Term not found.")
            return
        
        # Check for existing lessons on this day
        schedules = get_all_schedules_for_weekday(current_term.weekday)
        
        if schedules:
            # There are lessons scheduled, inform user to delete them first
            lessons_info = []
            for schedule in schedules:
                from database.students.crud import get_student
                student = get_student(schedule.student_id)
                student_name = f"{student.name} {student.surname}" if student else f"Student ID {schedule.student_id}"
                schedule_time = str(schedule.time) if hasattr(schedule.time, 'strftime') else schedule.time
                lessons_info.append(f"• {student_name} at {schedule_time}")
            
            lessons_msg = "\n".join(lessons_info)
            await update.message.reply_text(
                f"❌ Cannot set {current_term.weekday} as weekend.\n\n"
                f"<b>Lessons currently scheduled:</b>\n{lessons_msg}\n\n"
                f"Please delete or reschedule these lessons before setting this day as weekend.",
                parse_mode='HTML'
            )
            return
        
        # No lessons scheduled, proceed to set as weekend
        from database.terms.crud import update_term
        try:
            update_term(current_term.weekday, '00:00', '00:00')
            await update.message.reply_text(
                f"✅ <b>Day Set as Weekend!</b>\n\n"
                f"<b>Day:</b> {current_term.weekday}\n"
                f"<b>Status:</b> Working Day → Weekend\n"
                f"<b>Schedule:</b> 00:00 - 00:00",
                parse_mode='HTML'
            )
            
            # Return to terms menu
            await update.message.reply_text("Returning to Terms Management menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['terms'], resize_keyboard=True))
            context.user_data.pop('in_selecting_boundary', None)
            context.user_data.pop('in_change_terms_boundaries', None)
            context.user_data['in_terms_menu'] = True
            
        except Exception as e:
            logger.error(f"Error setting day as weekend: {e}")
            await update.message.reply_text("❌ Failed to set day as weekend. Please try again.")
        
        return
    elif selection not in ['START', 'END']:
        await update.message.reply_text("❌ Invalid selection. Please choose 'START', 'END', or 'WEEKEND':")
        return
    
    context.user_data['boundary_to_change'] = selection
    await update.message.reply_text(f"Please enter the new {selection.lower()} time (HH:MM):", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(f"{emoji('BACK')} BACK")]], resize_keyboard=True))
    context.user_data.pop('in_selecting_boundary', None)
    context.user_data['in_updating_boundary_time'] = True
    return

async def handle_updating_boundary_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == f"{emoji('BACK')} BACK":
        # Go back to boundary selection
        keyboard = [[KeyboardButton('START')],[KeyboardButton('END')],[KeyboardButton(f"{emoji('BACK')} BACK")]]
        await update.message.reply_text("Please select which boundary you want to change (START or END):", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        context.user_data.pop('in_updating_boundary_time', None)
        context.user_data['in_selecting_boundary'] = True
        return
    
    new_time = update.message.text
    
    # Validate time format
    if not re.match(r'^\d{2}:\d{2}$', new_time):
        await update.message.reply_text("❌ Invalid time format. Please enter the time in HH:MM format:")
        return
    
    # Validate time range
    if new_time < "08:00" or new_time > "21:00":
        await update.message.reply_text("❌ Time must be between 08:00 and 21:00. Please enter a valid time (HH:MM):")
        return
    
    # Get the current term
    from database.terms.crud import get_all_terms
    term_id = int(context.user_data['change_term_id'])
    all_terms = get_all_terms()
    current_term = next((t for t in all_terms if t.id == term_id), None)
    
    if not current_term:
        await update.message.reply_text("❌ Term not found. Returning to Terms Management menu.")
        context.user_data.pop('in_updating_boundary_time', None)
        context.user_data.pop('in_selecting_boundary', None)
        context.user_data.pop('in_change_terms_boundaries', None)
        context.user_data['in_terms_menu'] = True
        await update.message.reply_text("Returning to Terms Management menu.",reply_markup=ReplyKeyboardMarkup(earnings_keyboard['terms'], resize_keyboard=True))
        return
    
    # Convert time objects to strings for comparison
    old_start = str(current_term.start_time) if hasattr(current_term.start_time, 'strftime') else current_term.start_time
    old_end = str(current_term.end_time) if hasattr(current_term.end_time, 'strftime') else current_term.end_time
    boundary = context.user_data['boundary_to_change']
    
    # Check if this is a weekend (00:00 - 00:00) - need to set both boundaries
    is_weekend = old_start == "00:00:00" and old_end == "00:00:00"
    
    if is_weekend:
        # Store the first boundary and ask for the second
        if 'first_boundary_time' not in context.user_data:
            context.user_data['first_boundary_time'] = new_time
            context.user_data['first_boundary_type'] = boundary
            
            # Ask for the other boundary
            other_boundary = 'END' if boundary == 'START' else 'START'
            await update.message.reply_text(
                f"This day is currently set as weekend (00:00 - 00:00).\n"
                f"You've set {boundary} time to {new_time}.\n\n"
                f"Please enter the {other_boundary} time (HH:MM):",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton(f"{emoji('BACK')} BACK")]], resize_keyboard=True)
            )
            return
        else:
            # We have both boundaries now
            first_time = context.user_data['first_boundary_time']
            first_type = context.user_data['first_boundary_type']
            
            if first_type == 'START':
                new_start = first_time
                new_end = new_time
            else:
                new_start = new_time
                new_end = first_time
            
            # Validate start < end
            if new_start >= new_end:
                await update.message.reply_text(f"❌ Start time ({new_start}) must be before end time ({new_end}). Please enter a valid time:")
                return
            
            # Update both boundaries
            from database.terms.crud import update_term
            try:
                update_term(current_term.weekday, new_start, new_end)
                await update.message.reply_text(
                    f"✅ <b>Term Activated Successfully!</b>\n\n"
                    f"<b>Day:</b> {current_term.weekday}\n"
                    f"<b>Status:</b> Weekend → Working Day\n"
                    f"<b>New Schedule:</b> {new_start} - {new_end}",
                    parse_mode='HTML'
                )
                
                # Clean up temporary data
                context.user_data.pop('first_boundary_time', None)
                context.user_data.pop('first_boundary_type', None)
                
                # Stay in boundary selection menu
                keyboard = [[KeyboardButton('START')],[KeyboardButton('END')],[KeyboardButton(f"{emoji('BACK')} BACK")]]
                await update.message.reply_text(
                    "Would you like to change another boundary?",
                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                )
                context.user_data.pop('in_updating_boundary_time', None)
                context.user_data['in_selecting_boundary'] = True
                
            except Exception as e:
                logger.error(f"Error updating term: {e}")
                await update.message.reply_text("❌ Failed to update term. Please try again.")
                context.user_data.pop('first_boundary_time', None)
                context.user_data.pop('first_boundary_type', None)
            
            return
    
    # Normal case: updating one boundary on an already working day
    # Validate against the other boundary
    if boundary == 'START':
        if new_time >= old_end:
            await update.message.reply_text(f"❌ Start time must be before end time ({old_end}). Please enter a valid start time:")
            return
        new_start = new_time
        new_end = old_end
    else:  # END
        if new_time <= old_start:
            await update.message.reply_text(f"❌ End time must be after start time ({old_start}). Please enter a valid end time:")
            return
        new_start = old_start
        new_end = new_time
    
    # Validate against existing schedule
    from database.schedule.crud import get_all_schedules_for_weekday
    schedules = get_all_schedules_for_weekday(current_term.weekday)
    
    conflicts = []
    for schedule in schedules:
        schedule_time = str(schedule.time) if hasattr(schedule.time, 'strftime') else schedule.time
        if schedule_time < new_start or schedule_time >= new_end:
            from database.students.crud import get_student
            student = get_student(schedule.student_id)
            student_name = f"{student.name} {student.surname}" if student else f"Student ID {schedule.student_id}"
            conflicts.append(f"• {student_name} at {schedule_time}")
    
    if conflicts:
        conflict_msg = "\n".join(conflicts)
        await update.message.reply_text(
            f"❌ Cannot update {boundary.lower()} time to {new_time}.\n\n"
            f"<b>Conflicting lessons found:</b>\n{conflict_msg}\n\n"
            f"Please reschedule these lessons first or choose a different time.",
            parse_mode='HTML'
        )
        return
    
    # Update the term
    try:
        if boundary == 'START':
            from database.terms.crud import update_start_time
            update_start_time(term_id, new_time)
            change_msg = f"<b>Start time:</b> {old_start} → {new_time}"
        else:
            from database.terms.crud import update_end_time
            update_end_time(term_id, new_time)
            change_msg = f"<b>End time:</b> {old_end} → {new_time}"
        
        await update.message.reply_text(
            f"✅ <b>Term Updated Successfully!</b>\n\n"
            f"<b>Day:</b> {current_term.weekday}\n"
            f"{change_msg}\n"
            f"<b>New Schedule:</b> {new_start} - {new_end}",
            parse_mode='HTML'
        )
        
        # Stay in the boundary selection menu for more changes
        keyboard = [[KeyboardButton('START')],[KeyboardButton('END')],[KeyboardButton(f"{emoji('BACK')} BACK")]]
        await update.message.reply_text(
            "Would you like to change another boundary?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        context.user_data.pop('in_updating_boundary_time', None)
        context.user_data['in_selecting_boundary'] = True
        
    except Exception as e:
        logger.error(f"Error updating {boundary.lower()} time: {e}")
        await update.message.reply_text(f"❌ Failed to update {boundary.lower()} time. Please try again.")
    
    return