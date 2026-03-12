from telegram import KeyboardButton
from utils.config import Settings

emoji = Settings.emoji

#TODO: Implement get_lessons_keyboard function
def get_lessons_keyboard(period: str):
    pass

#TODO: Implement get_free_terms_keyboard function
def get_free_terms_keyboard(period: str):
    pass



earnings_keyboard = {
    'earnings': [
        [KeyboardButton(f"TUTOR")],
        [KeyboardButton(f"{emoji('BACK')} BACK")],
    ],
    'personal_student_menu': [
        [KeyboardButton(f'SCHEDULE')],
        [KeyboardButton(f'ADD PAYMENT')],
        [KeyboardButton(f'UPDATE STUDENT INFO')],
        [KeyboardButton(f'DELETE STUDENT')],
        [KeyboardButton(f'{emoji("BACK")} BACK')],
    ],
    'student_schedule_menu': [
        [KeyboardButton(f'ADD LESSON IN SCHEDULE')],
        [KeyboardButton(f'UPDATE LESSONS TIME')],
        [KeyboardButton(f'DELETE LESSON')],
        [KeyboardButton(f'{emoji("BACK")} BACK')],
    ],
    'update_student_info_menu': [
        [KeyboardButton(f'UPDATE PRICE')],
        [KeyboardButton(f'UPDATE NAME')],
        [KeyboardButton(f'UPDATE SURNAME')],
        [KeyboardButton(f'UPDATE PAYMENT FREQUENCY')],
        [KeyboardButton(f'DONE')],
        [KeyboardButton(f'{emoji("BACK")} BACK')],
    ],

    'payment_frequency': [
        [KeyboardButton(f'DAILY')],
        [KeyboardButton(f'WEEKLY')],
        [KeyboardButton(f'MONTHLY')],
        [KeyboardButton(f'{emoji("BACK")} BACK')],
        [KeyboardButton(f'{emoji("CANCEL")} CANCEL')]
    ],
    
    'default_back_cancel': [
        [KeyboardButton(f'{emoji("BACK")} BACK')],
        [KeyboardButton(f'{emoji("CANCEL")} CANCEL')]
    ], 

    'tutor': [
        [KeyboardButton(f"SCHEDULE ")],
        [KeyboardButton(f"STUDENTS")],
        [KeyboardButton(f'TERMS')],
        [KeyboardButton(f"PAYMENTS")],
        [KeyboardButton(f"{emoji('BACK')} BACK")],
    ],

    'students': [
        [KeyboardButton(f"ADD STUDENT")],
        [KeyboardButton(f"VIEW STUDENTS")],
        [KeyboardButton(f"{emoji('BACK')} BACK")],
    ],

    'schedule_period': [
        [KeyboardButton(f'TODAY')],
        [KeyboardButton(f'THIS WEEK')],
        [KeyboardButton(f'NEXT WEEK')],
        [KeyboardButton(f'THIS MONTH')],
        [KeyboardButton(f'{emoji("BACK")} BACK')],
    ],

    'lessons_today': get_lessons_keyboard('today'),
    'lessons_week': get_lessons_keyboard('week'),
    'lessons_month': get_lessons_keyboard('month'),
    'lesson' : [
        [KeyboardButton(f"COMPLETED")],
        [KeyboardButton(f"CHANGE TERM")],
        [KeyboardButton(f"CANCEL LESSON")],
        [KeyboardButton(f"{emoji('BACK')} BACK")],
    ],
    'change_lesson_term': [
        [KeyboardButton(f"FREE TERMS")],
        [KeyboardButton(f"SET NEW TERM")],
        [KeyboardButton(f"{emoji('BACK')} BACK")],
    ],
    'terms': [
        [KeyboardButton(f'FREE TERMS')],
        [KeyboardButton(f'SET TERMS BOUNDARIES')],
        [KeyboardButton(f'CHANGE TERMS BOUNDARIES')],
        [KeyboardButton(f'{emoji("BACK")} BACK')],
    ],
    'terms_with_boundaries': [
        [KeyboardButton(f'FREE TERMS')],
        [KeyboardButton(f'CHANGE TERMS BOUNDARIES')],
        [KeyboardButton(f'{emoji("BACK")} BACK')],
    ],
    'free_terms_period': [
        [KeyboardButton(f'TODAY')],
        [KeyboardButton(f'THIS WEEK')],
        [KeyboardButton(f'THIS MONTH')],
        [KeyboardButton(f'{emoji("BACK")} BACK')],
    ],
    'free_terms_today': get_free_terms_keyboard('today'),
    'free_terms_week': get_free_terms_keyboard('week'),
    'free_terms_month': get_free_terms_keyboard('month'),

    'back_cancel': [
        [KeyboardButton(f'{emoji("BACK")} BACK')],
        [KeyboardButton(f'{emoji("CANCEL")} CANCEL')],
    ],

}