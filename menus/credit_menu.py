from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.config import Settings

emoji = Settings.emoji
logger = Settings.LOGGER


FETCH_TOTAL_AMOUNT = 1
FETCH_CATEGORY = 2
FETCH_LENDER_NAME = 3
FETCH_START_DATE = 4
FETCH_END_DATE = 5
FETCH_MONTHLY_PAYMENT = 6
FETCH_LAST_PAYMENT = 7

def get_credit_menu():
    """Create credit menu keyboard with buttons"""
    
    keyboard = [
        [KeyboardButton(f"{emoji('NEW')} Add Credit/Loan")],
        [KeyboardButton(f"{emoji('MONEY')} Pay Credit/Loan")],
        [KeyboardButton(f"{emoji('DELETE')} Delete Credit/Loan")],
        [KeyboardButton(f"{emoji('STATS')} View Credit/Loan Statistics")],
    ]
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def show_credit_statistics():
    """Display detailed credit statistics"""
    from database.credit.services import get_credit_statistics, get_overall_credit_summary
    
    try:
        summary = get_overall_credit_summary()
        statistics = get_credit_statistics()
        
        if not statistics:
            return "📊 No credits found."
        
        # Overall summary
        lines = ["📊 Credit Statistics\n"]
        lines.append("=" * 45)
        lines.append(f"Total Credits: {summary['total_credits']}")
        lines.append(f"Total Borrowed: {summary['total_borrowed']:.2f} zl")
        lines.append(f"Total Paid: {summary['total_paid']:.2f} zl")
        lines.append(f"Remaining: {summary['total_remaining']:.2f} zl")
        lines.append(f"Progress: {summary['progress_percent']:.1f}%")
        lines.append("=" * 45)
        lines.append("")
        
        # Individual credits
        for credit in statistics:
            lines.append(f"💳 {credit['lender_name']} - {credit['category']}")
            lines.append(f"   Total: {credit['total_amount']:.2f} zl")
            lines.append(f"   Paid: {credit['total_paid']:.2f} zl ({credit['paid_payments']}/{credit['total_payments']} payments)")
            lines.append(f"   Remaining: {credit['remaining_amount']:.2f} zl")
            lines.append(f"   Progress: {credit['progress_percent']:.1f}%")
            
            if credit['next_payment_date']:
                next_date = credit['next_payment_date'].strftime('%d.%m.%Y') if hasattr(credit['next_payment_date'], 'strftime') else str(credit['next_payment_date'])
                lines.append(f"   Next Payment: {next_date} ({credit['monthly_payment']:.2f} zl)")
            
            lines.append("")
        
        message = "\n".join(lines)
        
        # Safety check for message length
        if len(message) > 4000:
            message = message[:4000] + "\n... (truncated)"
        
        return message
    except Exception as e:
        logger.error(f"Error showing credit statistics: {e}")
        return "❌ Error loading credit statistics."

def get_credits_list_keyboard():
    from database.credit.crud import get_credits
    credits = get_credits()
    keyboard = []
    for credit in credits:
        button_text = f"{credit.id} - {credit.lender_name} - {credit.category} - {credit.total_amount}"
        keyboard.append([KeyboardButton(button_text)])
    keyboard.append([KeyboardButton(f"{emoji('BACK')} Back")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def handle_credit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.text == f"{emoji('NEW')} Add Credit/Loan":
        flow = credit_flow(update, context, action_key='total_amount',credit_details=credit_data_actions['credit_details'].copy())
        return await flow
    
    elif update.message.text == 'CREDITS':
        await update.message.reply_text(
            f"<pre>{show_credit_info()}</pre>",
            parse_mode='HTML',
            reply_markup=get_credit_menu()
        )
    elif update.message.text == f"{emoji('MONEY')} Pay Credit/Loan":
        await update.message.reply_text("Feature to update credit/loan is under development.")
    elif update.message.text == f"{emoji('DELETE')} Delete Credit/Loan":
        context.user_data['delete_credit'] = True
        context.user_data.pop('in_credit_menu', None)
        await update.message.reply_text("Select the credit/loan you wish to delete.", reply_markup=get_credits_list_keyboard())
        
    elif context.user_data.get('delete_credit'):
        context.user_data.pop('delete_credit', None)
        from database.credit.crud import delete_credit, get_credits
        from database.credit_payment.crud import delete_credit_payment
        if update.message.text == f"{emoji('BACK')} Back":
            await update.message.reply_text("Deletion cancelled.", reply_markup=get_credit_menu())
            return
        text = update.message.text
        delete_credit(text.split(" - ")[0])  # Assuming lender_name is unique
        delete_credit_payment(text.split(" - ")[0])

        await update.message.reply_text(f"{emoji('DONE')} Credit/Loan deleted successfully!", reply_markup=get_credit_menu())

    elif update.message.text == f"{emoji('STATS')} View Credit/Loan Statistics":
        await update.message.reply_text(
            f"<pre>{show_credit_statistics()}</pre>",
            parse_mode='HTML',
            reply_markup=get_credit_menu()
        )
    elif update.message.text == f"{emoji('BACK')} BACK":
        from menus.main_menu import get_main_menu
        await update.message.reply_text(
            "Returning to main menu.",
            reply_markup=get_main_menu()
        )
    else:
        logger.warning(f"Unhandled credit menu option: {update.message.text}")
        await update.message.reply_text(f"{show_credit_info()}",reply_markup=get_credit_menu())



credit_data_actions = {'credit_details':{'user_id':None,
                                         'total_amount':None,
                                         'category':None,
                                         'lender_name':None,
                                         'start_date':None,
                                         'end_date':None,
                                         'monthly_payment':None,
                                         'last_payment':None,
                                         'status':False
                                         },
                        'total_amount':{'action':FETCH_TOTAL_AMOUNT,'prev':None,'next':'category','prompt':"Please enter the total amount of the credit/loan (in your currency):"},
                        'category':{'action':FETCH_CATEGORY,'prev':'total_amount','next':'lender_name','prompt':"Please enter the category for this credit/loan (e.g., 'Personal Loan', 'Mortgage'): "},
                        'lender_name':{'action':FETCH_LENDER_NAME,'prev':'category','next':'start_date','prompt':"Please enter the lender's name: "},
                        'start_date':{'action':FETCH_START_DATE,'prev':'lender_name','next':'end_date','prompt':"Please enter the start date of the credit/loan (YYYY-MM-DD): "},
                        'end_date':{'action':FETCH_END_DATE,'prev':'start_date','next':'monthly_payment','prompt':"Please enter the end date of the credit/loan (YYYY-MM-DD): "},
                        'monthly_payment':{'action':FETCH_MONTHLY_PAYMENT,'prev':'end_date','next':'last_payment','prompt':"Please enter the monthly payment amount (in your currency): "},
                        'last_payment':{'action':FETCH_LAST_PAYMENT,'prev':'monthly_payment','next':None,'prompt':"Please enter the amount of the last payment made (in your currency): "}
}

async def credit_flow(update: Update, context: ContextTypes.DEFAULT_TYPE, action_key: str, credit_details: dict):
    """Manage the flow of adding or updating credit/loan details"""
    context.user_data['credit_details'] = credit_details
    return await ask_credit_details(update, context, action_key)


async def start_credit_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiate the credit/loan addition flow"""
    context.user_data['credit_details'] = credit_data_actions['credit_details'].copy()
    return await credit_flow(update, context, action_key='total_amount',credit_details=context.user_data['credit_details'])

async def ask_credit_details(update: Update, context: ContextTypes.DEFAULT_TYPE, action_key: str):
    """Prompt user for credit/loan details based on the current stage"""
    await update.message.reply_text(f"{show_credit_flow_info(context)}")
    
    # For date fields, show inline keyboard instead of regular keyboard
    if action_key == 'start_date':
        from utils.Button import DatePickerKeyboard
        keyboard = DatePickerKeyboard.get_year_keyboard()
        context.user_data['date_field'] = 'start_date'
        context.user_data['awaiting_date_selection'] = True
        await update.message.reply_text(
            "Select the start year:",
            reply_markup=keyboard
        )
        return FETCH_START_DATE
    
    elif action_key == 'end_date':
        from utils.Button import DatePickerKeyboard
        keyboard = DatePickerKeyboard.get_year_keyboard()
        context.user_data['date_field'] = 'end_date'
        context.user_data['awaiting_date_selection'] = True
        await update.message.reply_text(
            "Select the end year:",
            reply_markup=keyboard
        )
        return FETCH_END_DATE
    
    # For non-date fields, use regular keyboards as before
    if action_key == 'total_amount':
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton(f"{emoji('CANCEL')} Cancel")]],
            resize_keyboard=True
        )
    else:
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton(f"{emoji('BACK')} Back")]],
            resize_keyboard=True
        )
    
    await update.message.reply_text(
        f'{credit_data_actions[action_key]["prompt"]}',
        reply_markup=reply_markup
    )
    return credit_data_actions[action_key]['action']

async def receive_total_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive total amount for credit/loan"""
    text = update.message.text
    
    # Check for Cancel button FIRST
    if text == f'{emoji("CANCEL")} Cancel':
        context.user_data.pop('credit_details', None)
        await update.message.reply_text("Credit/Loan addition cancelled.", reply_markup=get_credit_menu())
        return ConversationHandler.END  # Use ConversationHandler.END instead of -1
    
    # Then try to convert to float
    try:
        amount = float(text)
        context.user_data['credit_details']['total_amount'] = amount
        return await ask_credit_details(update, context, action_key='category')
    except ValueError:
        await update.message.reply_text("Invalid amount. Please enter a numeric value.")
        return FETCH_TOTAL_AMOUNT

async def receive_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive category for credit/loan"""
    category = update.message.text
    if category == f'{emoji("BACK")} Back':
        prev_key = credit_data_actions['category']['prev']
        return await ask_credit_details(update, context, action_key=prev_key)
    context.user_data['credit_details']['category'] = category
    return await ask_credit_details(update, context, action_key='lender_name')

async def receive_lender_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive lender name for credit/loan"""
    lender_name = update.message.text
    if lender_name == f'{emoji("BACK")} Back':
        prev_key = credit_data_actions['lender_name']['prev']
        return await ask_credit_details(update, context, action_key=prev_key)
    context.user_data['credit_details']['lender_name'] = lender_name
    return await ask_credit_details(update, context, action_key='start_date')

from utils.Button import DatePickerKeyboard

async def receive_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button during start date selection"""
    text = update.message.text
    if text == f'{emoji("BACK")} Back':
        prev_key = credit_data_actions['start_date']['prev']
        context.user_data.pop('awaiting_date_selection', None)
        context.user_data.pop('date_field', None)
        return await ask_credit_details(update, context, action_key=prev_key)
    # If not back button, ignore (date is set via callback)
    return FETCH_START_DATE

async def receive_end_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button during end date selection"""
    text = update.message.text
    if text == f'{emoji("BACK")} Back':
        prev_key = credit_data_actions['end_date']['prev']
        context.user_data.pop('awaiting_date_selection', None)
        context.user_data.pop('date_field', None)
        return await ask_credit_details(update, context, action_key=prev_key)
    # If not back button, ignore (date is set via callback)
    return FETCH_END_DATE

async def handle_credit_date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        context.user_data['credit_details'][date_field] = selected_date
        
        await query.edit_message_text(f"✅ Selected {date_field.replace('_', ' ')}: {selected_date}")
        
        # Move to next step based on which date was selected
        if date_field == 'start_date':
            return await ask_credit_details(update, context, action_key='end_date')
        elif date_field == 'end_date':
            return await ask_credit_details(update, context, action_key='monthly_payment')
    
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
    
    elif data == "date_cancel":
        await query.edit_message_text("❌ Date selection cancelled.")
        # Return to previous step
        if date_field == 'start_date':
            return await ask_credit_details(update, context, action_key='lender_name')
        elif date_field == 'end_date':
            return await ask_credit_details(update, context, action_key='start_date')
        
async def receive_monthly_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive monthly payment for credit/loan"""
    text = update.message.text
    
    if text == f'{emoji("BACK")} Back':
        prev_key = credit_data_actions['monthly_payment']['prev']
        return await ask_credit_details(update, context, action_key=prev_key)
    try:
        monthly_payment = float(text)
        context.user_data['credit_details']['monthly_payment'] = monthly_payment
        return await ask_credit_details(update, context, action_key='last_payment')
    except ValueError:
        await update.message.reply_text("Invalid amount. Please enter a numeric value.")
        return FETCH_MONTHLY_PAYMENT

async def receive_last_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive last payment amount for credit/loan"""
    text = update.message.text
    if text == f'{emoji("BACK")} Back':
        prev_key = credit_data_actions['last_payment']['prev']
        return await ask_credit_details(update, context, action_key=prev_key)
    
    try:
        last_payment_amount = float(text)
        context.user_data['credit_details']['last_payment'] = last_payment_amount
        
        from database.credit.crud import create_credit
        from database.credit.services import fill_credit_payments
        new_credit = create_credit(user_id=update.effective_user.id,
           total_amount=context.user_data['credit_details']['total_amount'],
           category=context.user_data['credit_details']['category'],
           lender_name=context.user_data['credit_details']['lender_name'],
           start_date=context.user_data['credit_details']['start_date'],
           end_date=context.user_data['credit_details']['end_date'],
           monthly_payment=context.user_data['credit_details']['monthly_payment'],
           last_payment=last_payment_amount,  # Add this
           last_payment_amount=last_payment_amount
           )
        fill_credit_payments(new_credit)
        await update.message.reply_text(f"{emoji('DONE')} Credit/Loan details recorded successfully!",reply_markup=get_credit_menu())
        return -1  # End of conversation
    except ValueError:
        await update.message.reply_text("Invalid amount. Please enter a numeric value.")
        return FETCH_LAST_PAYMENT

async def handle_credit_date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date picker callbacks for credit flow"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    date_field = context.user_data.get('date_field')
    
    if data.startswith("year_"):
        year = data.split("_")[1]
        context.user_data[f'{date_field}_year'] = year
        from utils.Button import DatePickerKeyboard
        keyboard = DatePickerKeyboard.get_month_keyboard(year)
        await query.edit_message_text(
            f"Year: {year}\nSelect month:",
            reply_markup=keyboard
        )
        # Stay in the same state
        if date_field == 'start_date':
            return FETCH_START_DATE
        else:
            return FETCH_END_DATE
    
    elif data.startswith("month_"):
        parts = data.split("_")
        year = parts[1]
        month = parts[2]
        context.user_data[f'{date_field}_month'] = month
        from utils.Button import DatePickerKeyboard
        keyboard = DatePickerKeyboard.get_day_keyboard(year, month)
        await query.edit_message_text(
            f"Year: {year}, Month: {month}\nSelect day:",
            reply_markup=keyboard
        )
        # Stay in the same state
        if date_field == 'start_date':
            return FETCH_START_DATE
        else:
            return FETCH_END_DATE
    
    elif data.startswith("day_"):
        # Day selected, date is complete
        parts = data.split("_")
        year = parts[1]
        month = parts[2]
        day = parts[3]
        selected_date = f"{year}-{month}-{day}"
        
        # Store the date
        context.user_data['credit_details'][date_field] = selected_date
        context.user_data.pop('awaiting_date_selection', None)
        
        await query.edit_message_text(f"✅ Selected {date_field.replace('_', ' ')}: {selected_date}")
        
        # Show updated info
        info_msg = show_credit_flow_info(context)
        await query.message.reply_text(f"{info_msg}")
        
        # Continue to next step and RETURN THE NEXT STATE
        if date_field == 'start_date':
            # Show date picker for end date
            from utils.Button import DatePickerKeyboard
            keyboard = DatePickerKeyboard.get_year_keyboard()
            context.user_data['date_field'] = 'end_date'
            context.user_data['awaiting_date_selection'] = True
            await query.message.reply_text(
                "Select the end year:",
                reply_markup=keyboard
            )
            return FETCH_END_DATE  # IMPORTANT: Return the next state
            
        elif date_field == 'end_date':
            # Show keyboard for monthly payment input
            reply_markup = ReplyKeyboardMarkup(
                [[KeyboardButton(f"{emoji('BACK')} Back")]],
                resize_keyboard=True
            )
            await query.message.reply_text(
                credit_data_actions['monthly_payment']["prompt"],
                reply_markup=reply_markup
            )
            return FETCH_MONTHLY_PAYMENT  # IMPORTANT: Return the next state
    
    elif data == "date_back_year":
        from utils.Button import DatePickerKeyboard
        keyboard = DatePickerKeyboard.get_year_keyboard()
        await query.edit_message_text("Select year:", reply_markup=keyboard)
        # Stay in the same state
        if date_field == 'start_date':
            return FETCH_START_DATE
        else:
            return FETCH_END_DATE
    
    elif data.startswith("date_back_month_"):
        year = data.split("_")[3]
        from utils.Button import DatePickerKeyboard
        keyboard = DatePickerKeyboard.get_month_keyboard(year)
        await query.edit_message_text(
            f"Year: {year}\nSelect month:",
            reply_markup=keyboard
        )
        # Stay in the same state
        if date_field == 'start_date':
            return FETCH_START_DATE
        else:
            return FETCH_END_DATE
    
    elif data == "date_cancel":
        await query.edit_message_text("❌ Date selection cancelled.")
        context.user_data.pop('awaiting_date_selection', None)
        await query.message.reply_text(
            "Returning to credit menu...",
            reply_markup=get_credit_menu()
        )
        return ConversationHandler.END
        
def show_credit_flow_info(context: ContextTypes.DEFAULT_TYPE):
    message = (f'Credit/Loan Flow Info:\n'
               f'Amount: {context.user_data["credit_details"]["total_amount"]}\n'
               f'Category: {context.user_data["credit_details"]["category"]}\n'
               f'Lender: {context.user_data["credit_details"]["lender_name"]}\n'
               f'Start Date: {context.user_data["credit_details"]["start_date"]}\n'
               f'End Date: {context.user_data["credit_details"]["end_date"]}\n'
               f'Monthly Payment: {context.user_data["credit_details"]["monthly_payment"]}\n'
               f'Last Payment: {context.user_data["credit_details"]["last_payment"]}\n'
               )
    return message 

def show_credit_info():
    from database.credit.services import get_unpaid_credit_payments_dict
    payments = get_unpaid_credit_payments_dict()
    
    if not payments:
        return "✅ No unpaid credit payments."
    
    # Limit to first 20 payments to avoid message length issues
    max_payments = 20
    payments_to_show = payments[:max_payments]
    
    # Column widths
    lender_w = 10
    category_w = 10
    amount_w = 9
    
    # Build message
    lines = ["📋 Nearest Unpaid Credit Payments\n"]
    lines.append(f"{'Lender':<{lender_w}} {'Category':<{category_w}} {'Amount':>{amount_w}} Date")
    lines.append("-" * 42)  # Fixed total width
    
    for payment in payments_to_show:
        lender = (payment['lender_name'] or 'N/A')[:lender_w]
        category = (payment['category'] or 'N/A')[:category_w]
        amount = payment['amount']
        payment_date = payment['payment_date'].strftime('%d.%m.%Y') if hasattr(payment['payment_date'], 'strftime') else str(payment['payment_date'])
        
        # Fixed: ensure date fits on same line, remove extra spaces
        lines.append(f"{lender:<{lender_w}} {category:<{category_w}} {amount:>6.2f} zl {payment_date}")
    
    lines.append("-" * 42)
    
    if len(payments) > max_payments:
        lines.append(f"\n... and {len(payments) - max_payments} more")
    else:
        lines.append(f"\n📊 Total: {len(payments)} unpaid payments")
    
    message = "\n".join(lines)
    
    # Safety check for message length
    if len(message) > 4000:
        message = message[:4000] + "\n... (truncated)"
    
    return message