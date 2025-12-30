from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.transactions.crud import (
    create_transaction,
    get_transactions)
from utils.decorators import is_authenticated



@is_authenticated
async def add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transaction = {"user_id":"", "shop":"", "amount":"", "category":""}
    
    pass