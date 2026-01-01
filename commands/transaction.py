
import datetime
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from database.accounts.crud import get_account_id_by_name
from database.transactions.crud import create_transaction
from database.transactions.services import get_all_categories, get_all_categories_from_account, get_user_shops_from_account
from menus.spendings_menu import WAITING_FOR_NEW_ACCOUNT_NAME, get_spendings_menu
from utils.decorators import is_authenticated

from utils.config import Settings
WAITING_FOR_AMOUNT = 1 
WAITING_FOR_NAME = 2
WAITING_FOR_CATEGORY = 3
WAITING_FOR_SHOP_NAME = 4
WAITING_FOR_DATE = 5


emoji = Settings.emoji

skip_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton(f"{emoji('SKIP')} Skip")],[KeyboardButton(f"{emoji('BACK')} Back")]],
    resize_keyboard=True
)

def get_categories_keyboard(context: ContextTypes.DEFAULT_TYPE):
    """Create categories keyboard"""
    account = context.user_data.get('current_account')
    default_categories = ['Food', 'Transport', 'Entertainment', 'Caffeine', 'Other']

    user_categories = get_all_categories_from_account(account, db.get_session())
    print("User categories:", user_categories)
    categories = list(set(set(default_categories) | set(user_categories)))
    keyboard = [[KeyboardButton(category)] for category in categories]
    keyboard.append([KeyboardButton(f"{emoji('BACK')} Back")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_shop_keyboard(context: ContextTypes.DEFAULT_TYPE):
    """Create shop keyboard (if needed)"""
    account = context.user_data.get('current_account')
    print(f"DEBUG: account_name = {account}")  # ✅ Add this
    
    shops = ['Zabka', 'Carrefour', 'Lidl', 'Biedronka', 'Other']
    user_shops = get_user_shops_from_account(account, db.get_session())
    print(f"DEBUG: User shops from DB = {user_shops}")  # ✅ Add this
    print(f"DEBUG: Default shops = {shops}")  # ✅ Add this
    
    shops = list(set(shops) | set(user_shops))  # ✅ Simplified - no need for set(set())
    print(f"DEBUG: Union shops = {shops}")  # ✅ Add this
    
    keyboard = [[KeyboardButton(shop)] for shop in shops]
    keyboard.append([KeyboardButton(f"{emoji('BACK')} Back")])
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
    if action_key == 'amount':
        await update.message.reply_text(f"📝 Current Transaction Info:\n{transaction_flow_info(context)}")
        return await ask_for(update, context, transaction, 'amount')
    elif action_key == 'name':
        await update.message.reply_text(f"📝 Current Transaction Info:\n{transaction_flow_info(context)}")
        return await ask_for(update, context, transaction, 'name')
    elif action_key == 'category':
        await update.message.reply_text(f"📝 Current Transaction Info:\n{transaction_flow_info(context)}")
        return await ask_for(update, context, transaction, 'category')
    elif action_key == 'shop':
        await update.message.reply_text(f"📝 Current Transaction Info:\n{transaction_flow_info(context)}")
        return await ask_for(update, context, transaction, 'shop')
    elif action_key == 'date':
        await update.message.reply_text(f"📝 Current Transaction Info:\n{transaction_flow_info(context)}")
        return await ask_for(update, context, transaction, 'date')
    elif action_key is None:
        account = context.user_data.get('current_account')
        # Save transaction to DB
        account_id = get_account_id_by_name(account, db.get_session())
        create_transaction(db.get_session(), update.effective_user.id,
                           account_id,
                           transaction['amount'],
                           transaction['category'],
                           transaction.get('shop'),
                           transaction.get('name'),
                           transaction.get('date'))
        
        await update.message.reply_text(
            f"✅ Transaction added to '{account}'!\n TRANSACTION INFO:\nPRODUCT NAME: {transaction.get('name')}\nAMOUNT: {transaction['amount']}\nCATEGORY: {transaction['category']}\nSHOP: {transaction.get('shop')}\nDATE: {transaction.get('date') if transaction.get('date') else datetime.now().strftime('%Y-%m-%d')}",
            reply_markup=get_spendings_menu(update, context)
        )
        context.user_data.pop('transaction', None)
        context.user_data.pop('current_account', None)
        return ConversationHandler.END



async def receive_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transaction = context.user_data.get('transaction', {})
    try:
        if update.message.text.strip() == f"{emoji('CANCEL')} Cancel":
            await update.message.reply_text(
                "❌ Transaction cancelled.",
                reply_markup=get_spendings_menu(update, context)
            )
            context.user_data.pop('transaction', None)
            context.user_data.pop('current_account', None)
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
    elif text == f"{emoji('BACK')} Back":
        prev = transaction_actions['name']['prev']
        context.user_data['transaction'][prev] = None
        return await transaction_flow(update, context, action_key=prev, transaction=context.user_data['transaction'])
    else:
        context.user_data['transaction']['name'] = text
    next = transaction_actions['name']['next']
    return await transaction_flow(update, context, action_key=next, transaction=context.user_data['transaction'])

async def receive_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == f"{emoji('BACK')} Back":
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
    elif text == f"{emoji('BACK')} Back":
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
        context.user_data['transaction']['date'] = None  # Will be set to current date in DB
    else:
        try:
            date_obj = datetime.strptime(text, "%Y-%m-%d")
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
            [[KeyboardButton("TODAY")],[KeyboardButton(f"{emoji('BACK')} Back")]],
            resize_keyboard=True
        )
    else:
        reply_markup = None
    
    await update.message.reply_text(
        f'{transaction_actions[action_key]["prompt"]}',
        reply_markup=reply_markup
    )
    return transaction_actions[action_key]['stage']