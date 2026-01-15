
import datetime
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from database.transactions.crud import create_transaction, update_transaction
from database.transactions.services import get_all_categories, get_all_categories_from_account, get_spendings, get_user_shops_from_account
from menus.account_view.delete_transaction_menu import get_delete_list_menu
from menus.account_view.view_menu import get_dates_menu
from utils.decorators import is_authenticated
from menus.account_view.view_menu import dates_keyboard
from database.transactions.services import get_sorted_categories_by_popularity, get_sorted_shops_by_popularity
from utils.config import Settings
from utils.utils import parse_date_range
WAITING_FOR_AMOUNT = 1 
WAITING_FOR_NAME = 2
WAITING_FOR_CATEGORY = 3
WAITING_FOR_SHOP_NAME = 4
WAITING_FOR_DATE = 5

WAITING_FOR_AMOUNT_UPDATE = 6
WAITING_FOR_NAME_UPDATE = 7
WAITING_FOR_CATEGORY_UPDATE = 8
WAITING_FOR_SHOP_NAME_UPDATE = 9
WAITING_FOR_DATE_UPDATE = 10

def get_update_dates_menu():
    return ReplyKeyboardMarkup(dates_keyboard, resize_keyboard=True)

emoji = Settings.emoji

skip_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton(f"{emoji('SKIP')} Skip")],[KeyboardButton(f"{emoji('BACK')} BACK")]],
    resize_keyboard=True
)

def get_categories_keyboard(context: ContextTypes.DEFAULT_TYPE):
    """Create categories keyboard"""
    default_categories = Settings.CATEGORIES
    sorted_categories = get_sorted_categories_by_popularity()
    print(f"DEBUG: Sorted categories = {sorted_categories}")
    categories = [cat for cat in sorted_categories]
    for cat in default_categories:
        if cat not in categories:
            categories.append(cat)
    keyboard = [[KeyboardButton(category)] for category in categories]
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_shop_keyboard(context: ContextTypes.DEFAULT_TYPE):
    """Create shop keyboard (if needed)"""

    sorted_user_shops = get_sorted_shops_by_popularity()
    print(f"DEBUG: Sorted user shops = {sorted_user_shops}")
    shops = [shop for shop in sorted_user_shops]
    for shop in Settings.SHOPS:
        if shop not in shops:
            shops.append(shop)
    keyboard = [[KeyboardButton(shop)] for shop in shops]
    keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    keyboard.append([KeyboardButton(f"{emoji('SKIP')} Skip")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

transaction_actions = {
    'transaction': {'amount': None,'name': None, 'shop': None, 'category': None},

    'amount': {'stage': WAITING_FOR_AMOUNT, 'next': 'name','prev':None, 'prompt': "Please enter an amount (e.g., 12.34):"},
    'name': {'stage': WAITING_FOR_NAME, 'next': 'category','prev':'amount', 'prompt': "Please enter the product name or press /skip:"},
    'category': {'stage': WAITING_FOR_CATEGORY, 'next': 'shop','prev':'name', 'prompt': "Please enter the category:"},
    'shop': {'stage': WAITING_FOR_SHOP_NAME, 'next': 'date','prev':'category', 'prompt': "Please enter the shop name or press /skip:"},
    'date': {'stage': WAITING_FOR_DATE, 'next': None,'prev':'shop', 'prompt': "Please enter the date (YYYY-MM-DD) or press TODAY"},
}

async def start_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the transaction flow"""
    transaction = {
        'amount': None,
        'name': None,
        'shop': None,
        'category': None
    }
    context.user_data['transaction'] = transaction
    return await transaction_flow(update, context, action_key='amount', transaction=transaction)

def transaction_flow_info(context: ContextTypes.DEFAULT_TYPE):
    return f'Amount: {context.user_data["transaction"].get("amount")}\n' \
           f'Name: {context.user_data["transaction"].get("name")}\n' \
           f'Category: {context.user_data["transaction"].get("category")}\n' \
           f'Shop: {context.user_data["transaction"].get("shop")}\n'

async def transaction_flow(update: Update, context: ContextTypes.DEFAULT_TYPE, action_key: str, transaction, skip_field=None):
    from menus.spendings_menu import get_spendings_menu
    if action_key:
        await update.message.reply_text(f"📝 Current Transaction Info:\n{transaction_flow_info(context)}")
        return await ask_for(update, context, transaction, action_key)
    elif action_key is None:
        # Save transaction to DB
        create_transaction( update.effective_user.id,
                           transaction['amount'],
                           transaction['category'],
                           transaction.get('shop'),
                           transaction.get('name'),
                           transaction.get('date'))
        
        await update.message.reply_text(
            f"✅ Transaction !\n TRANSACTION INFO:\nPRODUCT NAME: {transaction.get('name')}\nAMOUNT: {transaction['amount']} zl.\nCATEGORY: {transaction['category']}\nSHOP: {transaction.get('shop')}\n",
            reply_markup=get_spendings_menu(update, context)
        )
        context.user_data.pop('transaction', None)
        return ConversationHandler.END



async def receive_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transaction = context.user_data.get('transaction', {})
    try:
        if update.message.text.strip() == f"{emoji('CANCEL')} Cancel":
            from menus.spendings_menu import get_spendings_menu

            await update.message.reply_text(
                "❌ Transaction cancelled.",
                reply_markup=get_spendings_menu(update, context)
            )
            context.user_data.pop('transaction', None)
            return ConversationHandler.END
        amount = float(update.message.text.strip())
        context.user_data['transaction']['amount'] = amount
        next_action = transaction_actions['amount']['next']
        return await transaction_flow(update, context, action_key=next_action, transaction=context.user_data['transaction'])
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please enter a valid number:")
        return WAITING_FOR_AMOUNT

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    text = update.message.text.strip()
    if text == f"{emoji('SKIP')} Skip":
        context.user_data['transaction']['name'] = None
    elif text == f"{emoji('BACK')} BACK":
        prev = transaction_actions['name']['prev']
        context.user_data['transaction'][prev] = None
        return await transaction_flow(update, context, action_key=prev, transaction=context.user_data['transaction'])
    else:
        context.user_data['transaction']['name'] = text
    next = transaction_actions['name']['next']
    return await transaction_flow(update, context, action_key=next, transaction=context.user_data['transaction'])

async def receive_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == f"{emoji('BACK')} BACK":
        prev = transaction_actions['category']['prev']
        context.user_data['transaction'][prev] = None
        return await transaction_flow(update, context, action_key=prev, transaction=context.user_data['transaction'])
    category = update.message.text.strip()
    context.user_data['transaction']['category'] = category
    next = transaction_actions['category']['next']
    return await transaction_flow(update, context, action_key=next, transaction=context.user_data['transaction'])

async def receive_shop_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == f"{emoji('SKIP')} Skip":
        context.user_data['transaction']['shop'] = 'Other'
    elif text == f"{emoji('BACK')} BACK":
        prev = transaction_actions['shop']['prev']
        context.user_data['transaction'][prev] = None
        return await transaction_flow(update, context, action_key=prev, transaction=context.user_data['transaction'])
    else:
        context.user_data['transaction']['shop'] = text
    next = transaction_actions['shop']['next']
    return await transaction_flow(update, context, action_key=next, transaction=context.user_data['transaction'])

async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.upper() == "TODAY":
        today = datetime.datetime.now()
        context.user_data['transaction']['date'] = today
    elif text == f"{emoji('BACK')} BACK":
        prev = transaction_actions['date']['prev']
        context.user_data['transaction'][prev] = None
        return await transaction_flow(update, context, action_key=prev, transaction=context.user_data['transaction'])
    else:
        try:
            date_obj = datetime.datetime.strptime(text, "%Y-%m-%d")
            context.user_data['transaction']['date'] = date_obj
            return await transaction_flow(update, context, action_key=None, transaction=context.user_data['transaction'])
        except ValueError:
            await update.message.reply_text("❌ Invalid date format. Please enter the date in YYYY-MM-DD format or type TODAY:")
            return WAITING_FOR_DATE
    # All data collected, save transaction
    
    return await transaction_flow(update, context, action_key=None, transaction=context.user_data['transaction'])

async def ask_for(update: Update, context: ContextTypes.DEFAULT_TYPE, transaction, action_key: str):
    """Ask for the next field in the transaction flow"""
    if action_key == 'name':
        reply_markup = skip_keyboard
    elif action_key == 'category':
        reply_markup = get_categories_keyboard(context)
    elif action_key == 'amount':
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton(f"{emoji('CANCEL')} Cancel")]],
            resize_keyboard=True
        )
    elif action_key == 'shop':
        reply_markup = get_shop_keyboard(context)
    elif action_key == 'date':
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton("TODAY")],[KeyboardButton(f"{emoji('BACK')} BACK")]],
            resize_keyboard=True
        )
    else:
        reply_markup = None
    
    await update.message.reply_text(
        f'{transaction_actions[action_key]["prompt"]}',
        reply_markup=reply_markup
    )
    return transaction_actions[action_key]['stage']


# =================================================================================================
# UPDATE TRANSACTION FLOW
# =================================================================================================

# --------------------MENU KEYBOARDS--------------------
def get_updating_field_menu():
    updating_field_keyboard = [
        [KeyboardButton("AMOUNT")],
        [KeyboardButton("NAME")],
        [KeyboardButton("CATEGORY")],
        [KeyboardButton("SHOP")],
        [KeyboardButton("DATE")],
        [KeyboardButton("UPDATE TRANSACTION")],
        [KeyboardButton(f"{emoji('BACK')} BACK")]
    ]
    return ReplyKeyboardMarkup(updating_field_keyboard, resize_keyboard=True)

def get_update_list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update_list_keyboard = []
    start, end = parse_date_range(update=update, context=context, text=context.user_data.get('selected_date_range'))
    transaction_list = get_spendings(start_date=start, end_date=end)
    for row in transaction_list:
        # Format date as string without spaces
        date_str = row.date.strftime("%Y-%m-%d") if row.date else "N/A"
        # Use | as separator
        button_text = f"{row.id}|{row.name or 'Unnamed'}|{row.amount}|{row.shop or 'N/A'}|{row.category or 'N/A'}|{date_str}"
        update_list_keyboard.append([KeyboardButton(button_text)])
    update_list_keyboard.append([KeyboardButton(f"{emoji('BACK')} BACK")])
    return ReplyKeyboardMarkup(update_list_keyboard, resize_keyboard=True)




async def handle_transaction_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle updating a transaction"""
    text = update.message.text
    
    if not text:
        await update.message.reply_text(
            "❌ Invalid date selection. Please choose a valid option from the menu.",
            reply_markup=get_update_dates_menu()
        )
        return

    # Handle BACK button
    if text == f"{emoji('BACK')} BACK":
        from menus.spendings_menu import get_spendings_menu
        context.user_data.pop('date_range_updating', None)
        await update.message.reply_text(
            "BACK to account menu",
            reply_markup=get_spendings_menu(update, context)
        )
        return
    elif text in ["TODAY", "THIS WEEK", "LAST 7 DAYS", "THIS MONTH", "LAST MONTH", "THIS YEAR", "LAST YEAR"]:
        context.user_data['selected_date_range'] = text

        context.user_data['update_transaction'] = True
        context.user_data['date_range_updating'] = False

        await update.message.reply_text(
            f"How would you like to view your statistics?",
        reply_markup=get_update_list_menu(update=update, context=context))

async def handle_transaction_to_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == f"{emoji('BACK')} BACK":
        from menus.spendings_menu import get_spendings_menu
        context.user_data.pop('update_transaction', None)
        await update.message.reply_text(
            "BACK to account menu",
            reply_markup=get_spendings_menu(update, context)
        )
        return

    try:
        # Split by | instead of space
        data = text.split('|')
        transaction_id = int(data[0])
        name = data[1]
        amount = float(data[2])
        shop = data[3]
        category = data[4]
        date_str = data[5]
        
        transaction_to_update = {
            'id': transaction_id,
            'amount': amount,
            'name': name,
            'shop': shop,
            'category': category,
            'date': date_str
        }
        context.user_data['transaction'] = transaction_to_update  

        context.user_data['selecting_update_field'] = True  
        context.user_data.pop('update_transaction', None)
        await update.message.reply_text(
            f"📝 Transaction selected:\n{await updating_info(context)}\n\nSelect the field you want to update:",
            reply_markup=get_updating_field_menu()
        )
    except (ValueError, IndexError) as e:
        print(f"DEBUG: Parse error: {e}")
        print(f"DEBUG: text='{text}'")
        await update.message.reply_text(
            "❌ Invalid selection. Please choose a valid transaction from the list.",
            reply_markup=get_update_list_menu(update=update, context=context)
        )

async def handle_updating_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from database.transactions.crud import update_transaction
    from menus.spendings_menu import get_spendings_menu
    text = update.message.text
    

    if text == f"{emoji('BACK')} BACK":
        context.user_data.pop('selecting_update_field', None)
        await update.message.reply_text(
            "BACK to account menu",
            reply_markup=get_spendings_menu(update, context)
        )
        return
    elif text in ["AMOUNT", "NAME", "CATEGORY", "SHOP", "DATE"]:
        context.user_data['updating_field'] = text
        return await ask_for_update_field(update, context)
    elif text == "UPDATE TRANSACTION":
        print("DEBUG: UPDATE TRANSACTION button clicked!")  # Add this
        transaction = context.user_data.get('transaction')
        print(f"DEBUG: transaction = {transaction}")  # Add this
        if transaction is None:
            await update.message.reply_text(
                "❌ No transaction selected for updating.",
                reply_markup=get_spendings_menu(update, context)
            )
            return ConversationHandler.END
        transaction_id = transaction.get('id')
        print(f"DEBUG: transaction_id = {transaction_id}")
        update_transaction( transaction_id, transaction)
        print("DEBUG: Transaction updated in DB")  # Add this
        await update.message.reply_text(
            f"✅ Transaction updated!\n UPDATED TRANSACTION INFO:\nPRODUCT NAME: {transaction.get('name')}\nAMOUNT: {transaction['amount']} zl.\nCATEGORY: {transaction['category']}\nSHOP: {transaction.get('shop')}\n",
            reply_markup=get_spendings_menu(update, context)
        )
        context.user_data.pop('transaction', None)
        context.user_data.pop('selecting_update_field', None)
        return ConversationHandler.END
    else:
        return await handle_transaction_range_field(update, context)


async def handle_transaction_range_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['updating_field'] = update.message.text
    return await ask_for_update_field(update, context)

async def update_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == f"{emoji('BACK')} BACK":
        context.user_data['selecting_update_field'] = True  
        await update.message.reply_text(
            f"✅ Going back to previous field.\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
            reply_markup=get_updating_field_menu()
        )
        return ConversationHandler.END  # Exit conversation state
    else:
        context.user_data['transaction']['amount'] = float(update.message.text)
        context.user_data['selecting_update_field'] = True 
        await update.message.reply_text(
            f"✅ Amount updated to: {update.message.text}\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
            reply_markup=get_updating_field_menu()
        )
        return ConversationHandler.END  #

async def update_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == f"{emoji('BACK')} BACK":
        context.user_data['selecting_update_field'] = True  
        await update.message.reply_text(
            f"✅ Going back to previous field.\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
            reply_markup=get_updating_field_menu()
        )
        return ConversationHandler.END  # Exit conversation state
    context.user_data['transaction']['name'] = update.message.text
    await update.message.reply_text(
        f"✅ Name updated to: {update.message.text}\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
        reply_markup=get_updating_field_menu()
    )
    return ConversationHandler.END  # Exit conversation state

async def update_category(update: Update, context: ContextTypes.DEFAULT_TYPE):  
    text = update.message.text
    if text == f"{emoji('BACK')} BACK":
        context.user_data['selecting_update_field'] = True  
        await update.message.reply_text(
            f"✅ Going back to previous field.\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
            reply_markup=get_updating_field_menu()
        )
        return ConversationHandler.END  # Exit conversation state  
    context.user_data['transaction']['category'] = update.message.text
    context.user_data['selecting_update_field'] = True  # Set routing flag
    await update.message.reply_text(
        f"✅ Category updated to: {update.message.text}\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
        reply_markup=get_updating_field_menu()
    )
    return ConversationHandler.END  # Exit conversation state

async def update_shop_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == f"{emoji('BACK')} BACK":
        context.user_data['selecting_update_field'] = True  
        await update.message.reply_text(
            f"✅ Going back to previous field.\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
            reply_markup=get_updating_field_menu()
        )
        return ConversationHandler.END  # Exit conversation state
    context.user_data['transaction']['shop'] = update.message.text
    context.user_data['selecting_update_field'] = True  # Set routing flag
    await update.message.reply_text(
        f"✅ Shop updated to: {update.message.text}\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
        reply_markup=get_updating_field_menu()
    )
    return ConversationHandler.END  # Exit conversation state

async def update_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.upper() == "TODAY":
        today = datetime.datetime.now()
        context.user_data['transaction']['date'] = today
    elif text == f"{emoji('BACK')} BACK":
        context.user_data['selecting_update_field'] = True  
        await update.message.reply_text(
            f"✅ Going back to previous field.\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
            reply_markup=get_updating_field_menu()
        )
        return ConversationHandler.END  # Exit conversation state
    else:
        try:
            date_obj = datetime.datetime.strptime(text, "%Y-%m-%d")
            context.user_data['transaction']['date'] = date_obj
        except ValueError:
            await update.message.reply_text("❌ Invalid date format. Please enter the date in YYYY-MM-DD format or type TODAY:")
            return WAITING_FOR_DATE_UPDATE
    context.user_data['selecting_update_field'] = True  # Set routing flag
    await update.message.reply_text(
        f"✅ Date updated to: {text}\n\nSelect the next field to update or 'UPDATE TRANSACTION' to save changes.\n {await updating_info(context)}",
        reply_markup=get_updating_field_menu()
    )
    return ConversationHandler.END  # Exit conversation state

async def update_transaction_in_db(transaction_id: int, updated_data: dict):
    pass  # Implement the logic to update the transaction in the database

async def ask_for_update_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📝 Current Transaction Info:\n{await updating_info(context)}")
    if context.user_data['updating_field'] == "AMOUNT":
        
        await update.message.reply_text(f"Please enter the new amount:")
        return WAITING_FOR_AMOUNT_UPDATE
    elif context.user_data['updating_field'] == "NAME":
        await update.message.reply_text("Please enter the new name:")
        return WAITING_FOR_NAME_UPDATE
    elif context.user_data['updating_field'] == "CATEGORY":

        await update.message.reply_text(
            "Please enter the new category:",
            reply_markup=get_categories_keyboard(context)
        )
        return WAITING_FOR_CATEGORY_UPDATE
    elif context.user_data['updating_field'] == "SHOP":
        await update.message.reply_text(
            "Please enter the new shop name:",
            reply_markup=get_shop_keyboard(context)
        )
        return WAITING_FOR_SHOP_NAME_UPDATE
    elif context.user_data['updating_field'] == "DATE":
        await update.message.reply_text("Please enter the new date (YYYY-MM-DD) or type TODAY:",
                                        reply_markup=ReplyKeyboardMarkup(
                                            [[KeyboardButton("TODAY")],[KeyboardButton(f"{emoji('BACK')} BACK")]],
                                            resize_keyboard=True
                                        ))
        
        return WAITING_FOR_DATE_UPDATE
    
async def updating_info(context: ContextTypes.DEFAULT_TYPE):
    transaction = context.user_data.get('transaction', {})
    return f'Amount: {transaction.get("amount", "N/A")}\n' \
           f'Name: {transaction.get("name", "N/A")}\n' \
           f'Category: {transaction.get("category", "N/A")}\n' \
           f'Shop: {transaction.get("shop", "N/A")}\n'