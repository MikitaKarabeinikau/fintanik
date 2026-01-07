from telegram import ReplyKeyboardRemove, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database.budget.crud import create_catgory_budget_for_current_month, get_budget_id_by_category_for_current_month, get_budget_id_by_category_for_next_month
from database.budget.services import get_difference_between_budgets_and_spendings
from utils.config import Settings

emoji = Settings.emoji

def get_budget_menu():
    """Create budget menu keyboard with buttons"""
    keyboard = [
        [KeyboardButton('ADD BUDGET')],
        [KeyboardButton('VIEW BUDGETS')],
        [KeyboardButton('UPDATE BUDGETS')],
        [KeyboardButton('CLEAR BUDGET')],
        [KeyboardButton('DELETE BUDGETS')],
        [KeyboardButton(f"{emoji('BACK')} BACK")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def handle_budget_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == 'BUDGETS':
        # First time entering budget menu - show current budgets
        await update.message.reply_text(
            f"<pre>{show_current_budgets()}</pre>",
            parse_mode='HTML',
            reply_markup=get_budget_menu()
        )
        return
    
    elif text == 'DELETE BUDGETS':
        context.user_data['deleting_budgets'] = True
        await update.message.reply_text(
            "Choose the budget period to delete budgets for:",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("CURRENT MONTH")],
                    [KeyboardButton("NEXT MONTH")],
                    [KeyboardButton(f"{emoji('BACK')} BACK")]
                ],
                resize_keyboard=True
            )
        )
    
    elif context.user_data.get('deleting_budgets'):
        context.user_data.pop('deleting_budgets', None)
        context.user_data['budget_deleting_period'] = text
        context.user_data['selecting_budget_category_to_delete'] = True
        if text not in ['CURRENT MONTH', 'NEXT MONTH']:
            await update.message.reply_text(
                "❌ Invalid selection. Please choose a valid budget period.",
                reply_markup=get_budget_menu()
            )
            return
        elif text == 'CURRENT MONTH':
            from database.budget.crud import get_all_budgets_for_current_month
            keyboard = []
            categories = get_all_budgets_for_current_month()
            for budget in categories.keys():
                keyboard.append([KeyboardButton(budget)])
            keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "Select a category to delete budget for CURRENT MONTH:",
                reply_markup=reply_markup
            )
        elif text == 'NEXT MONTH':
            from database.budget.crud import get_all_budgets_for_next_month
            keyboard = []
            categories = get_all_budgets_for_next_month()
            if not categories:
                await update.message.reply_text(
                    "✅ No budgets set for next month yet!",
                    reply_markup=get_budget_menu()
                )
                context.user_data.pop('budget_deleting_period', None)
                return
            for budget in categories.keys():
                keyboard.append([KeyboardButton(budget)])
            keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "Select a category to delete budget for NEXT MONTH:",
                reply_markup=reply_markup
            )
    elif context.user_data.get('selecting_budget_category_to_delete'):
        selected_category = text
        from database.budget.crud import delete_category_budget, get_budget_id_by_category_for_current_month, get_budget_id_by_category_for_next_month
        if context.user_data.get('budget_deleting_period') == 'CURRENT MONTH':
            budget_id = get_budget_id_by_category_for_current_month(selected_category)
        elif context.user_data.get('budget_deleting_period') == 'NEXT MONTH':
            budget_id = get_budget_id_by_category_for_next_month(selected_category)
        delete_category_budget(budget_id)
        context.user_data.pop('selecting_budget_category_to_delete', None)
        context.user_data.pop('budget_deleting_period', None)
        await update.message.reply_text(
            f"✅ Budget for category '{selected_category}' has been deleted.",
            reply_markup=get_budget_menu()
        )
    
    elif text == 'CLEAR BUDGET':
        context.user_data['clearing_budgets'] = True
        await update.message.reply_text(
            "Choose the budget period to clear budgets for:",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("CURRENT MONTH")],
                    [KeyboardButton("NEXT MONTH")],
                    [KeyboardButton(f"{emoji('BACK')} BACK")]
                ],
                resize_keyboard=True
            )
        )
    
    elif context.user_data.get('clearing_budgets'):
        
        context.user_data.pop('clearing_budgets', None)
        context.user_data['budget_clearing_period'] = text
        context.user_data['selecting_budget_category_to_clear'] = True
        if text not in ['CURRENT MONTH', 'NEXT MONTH']:
            await update.message.reply_text(
                "❌ Invalid selection. Please choose a valid budget period.",
                reply_markup=get_budget_menu()
            )
            return
        elif text == 'CURRENT MONTH':
            from database.budget.crud import get_all_budgets_for_current_month
            keyboard = []
            categories = get_all_budgets_for_current_month()
            for budget in categories.keys():
                keyboard.append([KeyboardButton(budget)])
            keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "Select a category to clear budget for CURRENT MONTH:",
                reply_markup=reply_markup
            )
        elif text == 'NEXT MONTH':
            from database.budget.crud import get_all_budgets_for_next_month
            keyboard = []
            categories = get_all_budgets_for_next_month()
            if not categories:
                await update.message.reply_text(
                    "✅ No budgets set for next month yet!",
                    reply_markup=get_budget_menu()
                )
                context.user_data.pop('budget_clearing_period', None)
                return
            for budget in categories.keys():
                keyboard.append([KeyboardButton(budget)])
            keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "Select a category to clear budget for NEXT MONTH:",
                reply_markup=reply_markup
            )
    elif context.user_data.get('selecting_budget_category_to_clear'):
        selected_category = text
        from database.budget.crud import reset_budget, get_budget_id_by_category_for_current_month, get_budget_id_by_category_for_next_month
        if context.user_data.get('budget_clearing_period') == 'CURRENT MONTH':
            budget_id = get_budget_id_by_category_for_current_month(selected_category)
        elif context.user_data.get('budget_clearing_period') == 'NEXT MONTH':
            budget_id = get_budget_id_by_category_for_next_month(selected_category)
        reset_budget(budget_id)
        context.user_data.pop('selecting_budget_category_to_clear', None)
        context.user_data.pop('budget_clearing_period', None)
        await update.message.reply_text(
            f"✅ Budget for category '{selected_category}' has been cleared.",
            reply_markup=get_budget_menu()
        )
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
            "Select the budget period you want to set:",
            reply_markup=reply_markup
        )
    
    elif text == 'UPDATE BUDGETS':
        context.user_data['updating_budget'] = True


        keyboard = [
            [KeyboardButton("CURRENT MONTH")],
            [KeyboardButton("NEXT MONTH")],
            [KeyboardButton(f"{emoji('BACK')} BACK")]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "Select the budget period you want to update:",
            reply_markup=reply_markup
        )


    elif text == 'VIEW BUDGETS':
        await update.message.reply_text(
            f"<pre>{show_current_budgets()}</pre>",
            parse_mode='HTML',
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
    elif context.user_data.get('updating_budget'):
        selected_range = text
        context.user_data['budget_date_range'] = selected_range
        context.user_data.pop('updating_budget', None)
        context.user_data['selecting_budget_category_for_update'] = True

        from database.budget.services import get_unset_budgets_categories
        if selected_range == 'CURRENT MONTH':
            from database.budget.services import get_all_budgets_for_current_month
            categories = get_all_budgets_for_current_month()
            keyboard = []
            for budget in categories.keys():
                keyboard.append([KeyboardButton(budget)])
            keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                f"Select a category to update budget for {selected_range.replace('_', ' ').title()}:",
                reply_markup=reply_markup
        )
        elif selected_range == 'NEXT MONTH':
            from database.budget.crud import get_all_budgets_for_next_month
            categories = get_all_budgets_for_next_month()
            if not categories:
                await update.message.reply_text(
                    "✅ No budgets set for next month yet!",
                    reply_markup=get_budget_menu()
                )
                context.user_data.pop('selecting_budget_category_for_update', None)
                return
            keyboard = []
            for budget in categories.keys():
                keyboard.append([KeyboardButton(budget)])
            keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                f"Select a category to update budget for {selected_range.replace('_', ' ').title()}:",
                reply_markup=reply_markup
        )
                
        else:
            await update.message.reply_text(
                "✅ All categories have budgets set for the current month!",
                reply_markup=get_budget_menu()
            )
            return

    elif context.user_data.get('selecting_budget_category_for_update'):
        selected_category = text
        context.user_data['selected_budget_category_for_update'] = selected_category
        context.user_data.pop('selecting_budget_category_for_update', None)
        context.user_data['waiting_for_budget_amount_update'] = True

        # Remove keyboard while typing amount
        await update.message.reply_text(
            f"💰 Enter new budget amount for '{selected_category}' (e.g., 500.00):\n\n"
            f"Type /cancel to cancel budget update.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    elif context.user_data.get('waiting_for_budget_amount_update'):
        amount_text = text
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            if context.user_data.get('budget_date_range') == 'CURRENT MONTH':
                budget_id = get_budget_id_by_category_for_current_month(
                    context.user_data['selected_budget_category_for_update']
                )
            elif context.user_data.get('budget_date_range') == 'NEXT MONTH':
                budget_id = get_budget_id_by_category_for_next_month(
                    context.user_data['selected_budget_category_for_update']
                )
            from database.budget.crud import update_category_budget
            update_category_budget(budget_id, amount)
            context.user_data.pop('waiting_for_budget_amount_update', None)
            await update.message.reply_text(
                f"✅ Budget for category '{context.user_data['selected_budget_category_for_update']}' updated to {amount}.",
                reply_markup=get_budget_menu()
        )
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid amount. Please enter a positive number for the budget amount:"
            )
            return

        # Clear budget updating flags
        context.user_data.pop('selected_budget_category_for_update', None)
    
       # Handle category selection
    elif context.user_data.get('selecting_budget_category'):
        from database.budget.services import get_unset_budgets_categories
        unset_categories = get_unset_budgets_categories()
    
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
        return "No budgets set for the current month."
    
    # Find the longest category name for alignment
    max_category_length = max(len(category) for category in data.keys())
    
    message_lines = ["📊 Budgets vs Spendings\n"]
    message_lines.append(f"{'Category':<{max_category_length}} | Difference")
    message_lines.append("-" * (max_category_length + 15))
    
    for category, difference in sorted(data.items()):
        message_lines.append(f"{category:<{max_category_length}} | {difference:>10.2f}")
    
    return "\n".join(message_lines)