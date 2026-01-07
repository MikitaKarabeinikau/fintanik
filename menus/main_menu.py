from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from utils.decorators import is_authenticated
from utils.config import Settings

emoji = Settings.emoji

# TODO: v2.0.0 GET dynamic account list from DB and default list from config
def get_main_menu():
    """Create main menu keyboard with buttons"""

    keyboard = [
        [KeyboardButton('SPENDINGS')],
        [KeyboardButton(f'SAVINGS')],
        [KeyboardButton(f"BUDGETS")],
        [KeyboardButton(f"EARNINGS")],
        [KeyboardButton(f'{emoji("SETTINGS")} SETTINGS')],
        [KeyboardButton(f'{emoji("HELP")} HELP')],
        [KeyboardButton(f"{emoji('LOGOUT')} Logout")],
        
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# TODO: v2.0.0 Write abstract handler for different main menu buttons
@is_authenticated
async def handle_main_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from commands.transaction import handle_transaction_to_update, handle_transaction_range, handle_updating_field

    """Handle main menu button clicks"""
    text = update.message.text
    print(f"DEBUG main_menu: text='{text}', flags={context.user_data.keys()}")  # Add this
    if text == f"{emoji('STATS')} View Statistics":
        from menus.account_view import view_menu  
        context.user_data['viewing_stats'] = True  # Set flag
        await update.message.reply_text(
            "📊 Select time period:",
            reply_markup=view_menu.get_dates_menu()
        )
        return 


    # Add this check BEFORE the current_account check

    # if context.user_data.get()
       
    if context.user_data.get('date_range_updating'):
        print(f"🔍 MAIN_MENU: date_range_updating flag detected! Calling handle_transaction_range")
        return await handle_transaction_range(update, context)
    if context.user_data.get('viewing_stats'):
        from menus.account_view import view_menu
        return await view_menu.handle_date_selection(update, context)
    if context.user_data.get('viewing_groups'):
        from menus.account_view import groups_menu
        return await groups_menu.handle_groups_menu(context, update)
    if context.user_data.get('deleting_transaction'):
        from menus.account_view.delete_transaction_menu import handle_delete_transaction_menu
        return await handle_delete_transaction_menu(update, context)
    if context.user_data.get('delete_list_menu'):
        from menus.account_view.delete_transaction_menu import handle_transaction_to_delete
        return await handle_transaction_to_delete(update, context)
 
    if context.user_data.get('selecting_update_field'):
        from commands.transaction import handle_updating_field
        return await handle_updating_field(update, context)
    
    if context.user_data.get('update_transaction'):
        return await handle_transaction_to_update(update, context)

    if text.startswith(f"{emoji('MONEY')}") :
        from menus.spendings_menu import handle_spendings_menu
        return await handle_spendings_menu(update, context)
    

    elif text == 'SPENDINGS':
        from menus.spendings_menu import handle_spendings_menu
        return await handle_spendings_menu(update, context)
    # Handle all spendings menu buttons TODO: v2.0.0 Refactor into separate handler
    elif text in [f"{emoji('NEW')} Add Transaction", 
                f"{emoji('UPDATE')} Update Transaction",
                f"{emoji('DELETE')} Delete Transaction",
                f"{emoji('INVITE')} Invite User"]:
        from menus.spendings_menu import handle_spendings_menu
        return await handle_spendings_menu(update, context)


    elif text == 'SAVINGS':
        update.message.reply_text("💰 Savings feature coming soon!")
        return
    elif text == 'BUDGETS':
        from menus.budget_menu import handle_budget_menu
        context.user_data['in_budget_menu'] = True
        return await handle_budget_menu(update, context)
    
    elif context.user_data.get('in_budget_menu'):
        from menus.budget_menu import handle_budget_menu
        return await handle_budget_menu(update, context)

    elif text == 'EARNINGS':
        update.message.reply_text("💵 Earnings feature coming soon!")
        return
    elif text == f"{emoji('SETTINGS')} SETTINGS":
        from commands.settings import settings_command
        return await settings_command(update, context)
    
    elif text == f'{emoji('HELP')} HELP':
        from commands.help import help_command
        return await help_command(update, context)

    elif text == f"{emoji('LOGOUT')} Logout":
        from commands.logout import logout_command
        return await logout_command(update, context)
    
    else:
        await update.message.reply_text(
            "Please use the menu buttons below.",
            reply_markup=get_main_menu()
        )