from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import is_authenticated

@is_authenticated
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 *Available Commands:*

/start - Start the bot
/addexpense - Add a new expense
/stats - View your statistics
/categories - View all categories
/help - Show this help message

💡 *Tips:*
• Use buttons for quick input
• Track spending by category
• View weekly/monthly reports
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')