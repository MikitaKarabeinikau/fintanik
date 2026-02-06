def get_students_overview():
    """Display overview of all students with key information in table format"""
    from database.students.crud import get_all_students
    from database.schedule.crud import get_schedules_by_student
    from database.models import Lessons, Schedules
    from database import db
    from datetime import datetime
    from calendar import monthrange
    
    students = get_all_students()
    
    if not students:
        return "<b>👥 Students Overview:</b>\n\nNo students registered yet."
    
    # Calculate current month boundaries
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    _, last_day = monthrange(now.year, now.month)
    month_end = datetime(now.year, now.month, last_day, 23, 59, 59)
    
    # Calculate overall totals
    total_balance = sum(s.balance for s in students)
    
    # Calculate monthly earnings
    session = db.get_session()
    monthly_earnings_paid = 0
    monthly_earnings_unpaid = 0
    
    for student in students:
        schedules = get_schedules_by_student(student.id)
        for schedule in schedules:
            # Get lessons for this schedule in current month
            lessons = session.query(Lessons).filter(
                Lessons.schedule_id == schedule.id,
                Lessons.date >= month_start,
                Lessons.date <= month_end,
                Lessons.complited == True
            ).all()
            
            for lesson in lessons:
                if lesson.paid:
                    monthly_earnings_paid += student.lesson_price
                else:
                    monthly_earnings_unpaid += student.lesson_price
    
    total_monthly_earnings = monthly_earnings_paid + monthly_earnings_unpaid
    
    response = "<b>👥 Students: {}</b>\n\n".format(len(students))
    response += f"<b>📊 {now.strftime('%B %Y')}:</b>\n"
    response += f"💰 Total: {total_monthly_earnings:.2f} zł\n"
    response += f"✅ Paid: {monthly_earnings_paid:.2f} zł\n"
    response += f"❌ Not Paid: {monthly_earnings_unpaid:.2f} zł\n\n"
    
    # Sort students by name
    students_sorted = sorted(students, key=lambda s: s.name)
    
    # Build compact table
    response += "<pre>"
    response += "┌─────────────┬────┬─────┬──┐\n"
    response += "│ Student     │ Pr │ Bal │ L│\n"
    response += "├─────────────┼────┼─────┼──┤\n"
    
    for student in students_sorted:
        # Get schedule count
        schedules = get_schedules_by_student(student.id)
        schedule_count = len(schedules) if schedules else 0
        
        # Format name with shortened surname (max 11 chars)
        surname_short = student.surname[:3].upper()
        full_name = f"{student.name} {surname_short}."
        if len(full_name) > 11:
            # Shorten first name
            name_short = student.name[:7]
            full_name = f"{name_short}. {surname_short}."
        
        # Balance string (max 5 chars)
        if student.balance < 0:
            balance_str = f"{int(student.balance)}"
        elif student.balance > 0:
            balance_str = f"+{int(student.balance)}"
        else:
            balance_str = "0"
        
        # Keep balance to max 5 chars
        if len(balance_str) > 5:
            balance_str = balance_str[:5]
        
        response += f"│ {full_name:<11} │{int(student.lesson_price):>3} │{balance_str:>5} │{schedule_count:>2}│\n"
    
    response += "└─────────────┴────┴─────┴──┘\n"
    response += f"Total Balance: {int(total_balance)} zł"
    response += "</pre>"
    
    return response