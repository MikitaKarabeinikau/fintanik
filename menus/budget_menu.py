from telegram import ReplyKeyboardRemove, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database.budget.crud import create_catgory_budget_for_current_month
from database.budget.services import get_difference_between_budgets_and_spendings
from utils.config import Settings

emoji = Settings.emoji

def get_budget_menu():
    """Create budget menu keyboard with buttons"""
    keyboard = [
        [KeyboardButton('ADD BUDGET')],
        [KeyboardButton('VIEW BUDGETS')],
        [KeyboardButton(f"{emoji('BACK')} BACK")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def handle_budget_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == 'BUDGETS':
        # First time entering budget menu - show current budgets
        await update.message.reply_text(
            show_current_budgets(),
            reply_markup=get_budget_menu()
        )
        return

    elif text == 'ADD BUDGET':
        from database.budget.services import get_unset_budgets_categories
        user_telegram_id = update.effective_user.id
        unset_categories = get_unset_budgets_categories()
        if not unset_categories:
            await update.message.reply_text(
                "✅ All categories have budgets set for the current month!",
                reply_markup=get_budget_menu()
            )
            return
        
        context.user_data['selecting_budget_range'] = True

        # Show categories as keyboard buttons
        keyboard = [
            [KeyboardButton("CURRENT MONTH")],
            [KeyboardButton("NEXT MONTH")],
        ]
        keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Select a category to set a budget for the current month:",
            reply_markup=reply_markup
        )
    
    elif text == 'VIEW BUDGETS':
        await update.message.reply_text(
            show_current_budgets(),
            reply_markup=get_budget_menu()
        )
    
    elif text == f"{emoji('BACK')} BACK":
        from menus.main_menu import get_main_menu
        context.user_data.pop('in_budget_menu', None)
        await update.message.reply_text(
            "Back to main menu",
            reply_markup=get_main_menu()
        )

    elif context.user_data.get('selecting_budget_range'):
        selected_range = text
        context.user_data['budget_date_range'] = selected_range
        context.user_data.pop('selecting_budget_range', None)
        context.user_data['selecting_budget_category'] = True

        from database.budget.services import get_unset_budgets_categories
        unset_categories = get_unset_budgets_categories()
        if not unset_categories:
            await update.message.reply_text(
                "✅ All categories have budgets set for the current month!",
                reply_markup=get_budget_menu()
            )
            return

        # Show categories as keyboard buttons
        keyboard = [[KeyboardButton(category)] for category in unset_categories]
        keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"Select a category to set a budget for {selected_range.replace('_', ' ').title()}:",
            reply_markup=reply_markup
        )

       # Handle category selection
    elif context.user_data.get('selecting_budget_category'):
        from database.budget.services import get_unset_budgets_categories
        unset_categories = get_unset_budgets_categories()
        
        if text in unset_categories:
            # Store selected category and ask for amount
            context.user_data['selected_budget_category'] = text
            context.user_data['waiting_for_budget_amount'] = True
            context.user_data.pop('selecting_budget_category', None)
            
            # Remove keyboard while typing amount
            await update.message.reply_text(
                f"💰 Enter budget amount for '{text}' (e.g., 500.00):\n\n"
                f"Type /cancel to cancel budget creation.",
                reply_markup=ReplyKeyboardRemove()
            )
            return

    elif context.user_data.get('waiting_for_budget_amount'):
        if context.user_data.get('budget_date_range') == 'CURRENT MONTH':
            amount_text = text
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError("Amount must be positive.")
                create_catgory_budget_for_current_month(
                    update.effective_user.id,
                    context.user_data['selected_budget_category'], amount
                )
                context.user_data.pop('waiting_for_budget_amount', None)
                await update.message.reply_text(
                    f"✅ Budget of {amount} set for category '{context.user_data['selected_budget_category']}' for the current month.",
                    reply_markup=get_budget_menu()
        )
            except ValueError:
                await update.message.reply_text(
                    "❌ Invalid amount. Please enter a positive number for the budget amount:"
                )
                return
        elif context.user_data.get('budget_date_range') == 'NEXT MONTH':
            amount_text = text
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError("Amount must be positive.")
                from database.budget.crud import create_category_budget_for_next_month
                create_category_budget_for_next_month(
                    update.effective_user.id,
                    context.user_data['selected_budget_category'], amount
                )
                context.user_data.pop('waiting_for_budget_amount', None)
                await update.message.reply_text(
                    f"✅ Budget of {amount} set for category '{context.user_data['selected_budget_category']}' for next month.",
                    reply_markup=get_budget_menu()
        )
            except ValueError:
                await update.message.reply_text(
                    "❌ Invalid amount. Please enter a positive number for the budget amount:"
                )
                return
        

       

        # Clear budget setting flags
        context.user_data.pop('setting_budget_amount', None)
        context.user_data.pop('selected_budget_category', None)
    
    else:
        await update.message.reply_text(
            "Please use the menu buttons below.",
            reply_markup=get_budget_menu()
        )


def show_current_budgets():
    data = get_difference_between_budgets_and_spendings()
    if not data:
        return "📊 No budgets set for the current month."
    message_lines = ["📊 Current Budgets vs Spendings:\n"]
    for category, difference in data.items():
        message_lines.append(f"- {category}: {difference}")
    return "\n".join(message_lines)