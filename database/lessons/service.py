from datetime import datetime, timedelta
from calendar import monthrange
from database import db
from database.lessons.crud import create_lesson
from database.models import Lessons, Schedules, Students
from database.models import Lessons
from utils.config import Settings

logger = Settings.LOGGER


def generate_lesson_dates(weekday: str, time_str: str):
    """
    Generate all lesson dates for a given weekday from now until end of next month.
    
    Args:
        weekday: Weekday name (e.g., 'Monday', 'Tuesday', etc.)
        time_str: Time string (e.g., '14:00')
    
    Returns:
        list: List of datetime objects for all lesson occurrences
    """
    # Map weekday names to numbers (Monday=0, Sunday=6)
    weekday_map = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
        'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    
    target_weekday = weekday_map.get(weekday)
    if target_weekday is None:
        logger.error(f"Invalid weekday: {weekday}")
        return []
    
    # Parse time
    lesson_time = datetime.strptime(time_str, "%H:%M").time()
    
    # Get current date and calculate end of next month
    today = datetime.now().date()
    current_month = today.month
    current_year = today.year
    
    # Calculate next month
    next_month = current_month + 1 if current_month < 12 else 1
    next_year = current_year if current_month < 12 else current_year + 1
    
    # Get last day of next month
    _, last_day_next_month = monthrange(next_year, next_month)
    end_date = datetime(next_year, next_month, last_day_next_month).date()
    
    # Generate all dates for the target weekday
    lesson_dates = []
    current_date = today
    
    # Find the first occurrence of the target weekday from today
    days_ahead = target_weekday - current_date.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    
    first_occurrence = current_date + timedelta(days=days_ahead)
    
    # Generate all occurrences until end of next month
    lesson_date = first_occurrence
    while lesson_date <= end_date:
        # Combine date with time
        lesson_datetime = datetime.combine(lesson_date, lesson_time)
        lesson_dates.append(lesson_datetime)
        lesson_date += timedelta(weeks=1)  # Move to next week
    
    logger.info(f"Generated {len(lesson_dates)} lesson dates for {weekday} at {time_str}")
    return lesson_dates


def create_lessons_from_schedule(schedule_id: int, weekday: str, time_str: str):
    """
    Create lesson records for all occurrences of a schedule.
    
    Args:
        schedule_id: The schedule ID
        weekday: Weekday name (e.g., 'Monday')
        time_str: Time string (e.g., '14:00')
        
    Returns:
        int: Number of lessons created
    """
    lesson_dates = generate_lesson_dates(weekday, time_str)
    
    created_count = 0
    for lesson_date in lesson_dates:
        try:
            create_lesson(schedule_id=schedule_id, date=lesson_date, paid=False, complited=False)
            created_count += 1
        except Exception as e:
            logger.error(f"Failed to create lesson for {lesson_date}: {e}")
    
    logger.info(f"Created {created_count} lessons for schedule_id={schedule_id}")
    return created_count

def get_lessons_by_period(period: str):
    """
    Retrieve lessons based on the specified period.
    
    Args:
        period: 'today', 'week', or 'month'
        
    Returns:
        list: List of lesson records
    """
    period = period.lower()
    now = datetime.now()
    
    if period == 'today':
        start = datetime(now.year, now.month, now.day)
        end = start + timedelta(days=1)
    elif period == 'week':
        start = datetime(now.year, now.month, now.day) - timedelta(days=now.weekday())
        end = start + timedelta(weeks=1)
    elif period == 'next_week':
        start = datetime(now.year, now.month, now.day) - timedelta(days=now.weekday()) + timedelta(weeks=1)
        end = start + timedelta(weeks=1)
    elif period == 'month':
        start = datetime(now.year, now.month, 1)
        _, last_day = monthrange(now.year, now.month)
        end = datetime(now.year, now.month, last_day) + timedelta(days=1)
    else:
        logger.error(f"Invalid period: {period}")
        return []
    
    logger.info(f"Querying lessons for period '{period}': start={start}, end={end}")
    
    try:
        session = db.get_session()
        lessons = session.query(Lessons).filter(Lessons.date >= start, Lessons.date < end).order_by(Lessons.date).all()
        logger.info(f"Retrieved {len(lessons)} lessons for period '{period}'")
        
        # Debug: show what lessons were found
        for lesson in lessons:
            logger.info(f"  Lesson ID {lesson.id}: date={lesson.date}, schedule_id={lesson.schedule_id}")
        
        return lessons
    except Exception as e:
        logger.error(f"Error retrieving lessons for period '{period}': {e}")
        raise
    finally:
        session.close()

def get_lessons_with_student_info(period: str):
    """
    Retrieve lessons along with associated student information for a given period.
    
    Args:
        period: 'today', 'week', or 'month'
        
    Returns:
        list: List of tuples (Lesson, Student)
    """
    lessons = get_lessons_by_period(period)
    lessons_with_students = []
    
    try:
        session = db.get_session()
        for lesson in lessons:
            schedule = session.query(Schedules).filter_by(id=lesson.schedule_id).first()
            student = session.query(Students).filter_by(id=schedule.student_id).first()
            lessons_with_students.append((lesson, student))
        logger.info(f"Retrieved {len(lessons_with_students)} lessons with student info for period '{period}'")
        return lessons_with_students
    except Exception as e:
        logger.error(f"Error retrieving lessons with student info for period '{period}': {e}")
        raise
    finally:
        session.close()     