from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import calendar


class DatePickerKeyboard:
    """Create date picker keyboards with year, month, and day selection"""
    
    @staticmethod
    def get_year_keyboard():
        """Create keyboard for year selection (current year to +10 years)"""
        current_year = datetime.now().year
        keyboard = []
        row = []
        
        for i in range(11):  # Current year + 10 years
            year = current_year + i
            row.append(InlineKeyboardButton(str(year), callback_data=f"year_{year}"))
            
            # Create rows of 3 years each
            if len(row) == 3:
                keyboard.append(row)
                row = []
        
        # Add remaining years if any
        if row:
            keyboard.append(row)
        
        # Add cancel button
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="date_cancel")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_month_keyboard(year):
        """Create keyboard for month selection (01-12)"""
        keyboard = []
        row = []
        
        months = [
            ("Jan", "01"), ("Feb", "02"), ("Mar", "03"),
            ("Apr", "04"), ("May", "05"), ("Jun", "06"),
            ("Jul", "07"), ("Aug", "08"), ("Sep", "09"),
            ("Oct", "10"), ("Nov", "11"), ("Dec", "12")
        ]
        
        for month_name, month_num in months:
            row.append(InlineKeyboardButton(
                f"{month_name}", 
                callback_data=f"month_{year}_{month_num}"
            ))
            
            # Create rows of 3 months each
            if len(row) == 3:
                keyboard.append(row)
                row = []
        
        # Add navigation buttons
        keyboard.append([
            InlineKeyboardButton("⬅️ Back", callback_data="date_back_year"),
            InlineKeyboardButton("❌ Cancel", callback_data="date_cancel")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_day_keyboard(year, month):
        """Create keyboard for day selection based on year and month"""
        keyboard = []
        row = []
        
        # Get number of days in the month
        num_days = calendar.monthrange(int(year), int(month))[1]
        
        for day in range(1, num_days + 1):
            day_str = f"{day:02d}"  # Format as 2 digits
            row.append(InlineKeyboardButton(
                day_str,
                callback_data=f"day_{year}_{month}_{day_str}"
            ))
            
            # Create rows of 7 days (like a calendar week)
            if len(row) == 7:
                keyboard.append(row)
                row = []
        
        # Add remaining days if any
        if row:
            keyboard.append(row)
        
        # Add navigation buttons
        keyboard.append([
            InlineKeyboardButton("⬅️ Back", callback_data=f"date_back_month_{year}"),
            InlineKeyboardButton("❌ Cancel", callback_data="date_cancel")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_date(year, month, day):
        """Format the selected date as YYYY-MM-DD"""
        return f"{year}-{month}-{day}"


# Example usage functions
async def ask_for_date(update, context, message="Please select a date:"):
    """Start date selection process"""
    keyboard = DatePickerKeyboard.get_year_keyboard()
    await update.message.reply_text(message, reply_markup=keyboard)


async def handle_date_callback(update, context):
    """Handle date picker callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("year_"):
        # Year selected, show months
        year = data.split("_")[1]
        context.user_data['selected_year'] = year
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
        context.user_data['selected_month'] = month
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
        selected_date = DatePickerKeyboard.format_date(year, month, day)
        
        await query.edit_message_text(f"✅ Selected date: {selected_date}")
        
        # Store the date in context or process it
        context.user_data['selected_date'] = selected_date
        
        # Return the date or trigger next action
        return selected_date
    
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