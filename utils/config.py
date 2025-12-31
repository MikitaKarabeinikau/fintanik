import os 
from dotenv import load_dotenv
import logging 

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Settings:
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_default_token')
    BOT_PASSWORD = os.getenv('BOT_PASSWORD', 'default_password')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot_database.db')
    PASSWORD = os.getenv('BOT_PASSWORD', 'default_password')
    LOGGER = logger

    @staticmethod
    def emoji(name):
        emoji_map = {
            'FOOD': '🍔',
            'TRANSPORT': '🚗',
            'SWEETS': '🍰',
            'HEALTH': '💊',
            'HOUSEHOLD': '🏠',
            'CLOTHING': '👗',
            'HYGIENE': '🧼',
            'ENTERTAINMENT': '🎮',
            'UTILITIES': '💡',
            'ELECTRONICS': '📱',
            'OTHERS': '🛍️',
            'BACK': '🔙',
            'CANCEL': '❌',
            'NEW': '➕',
            'MONEY': '💰',
            'STATS': '📊',
            'LOGOUT': '🚪',
            'WELCOME': '👋',
            'DONE': '✅',
            'ACCOUNT': '🏦',
            'SETTINGS': '⚙️',
            'UPDATE': '✏️',
            'DELETE': '🗑️',
            'INVITE': '📨',
        }
        return emoji_map.get(name.upper(), '')

# =============================================================================
# ACCOUNT TYPES
# =============================================================================
    # TODO: v2.0.0 ADD more account types like 'savings', 'credit', 'earning'
    ACCOUNT_TYPES= ['spending']


# =============================================================================
# TEXT CONSTANTS
# =============================================================================
    @staticmethod
    def first_greet_text(username):
        return (
            f"👋 Welcome {username}!\n\n"
                "Available commands:\n"
                "/addexpense - Add a new expense\n"
                "/stats - View your statistics\n"
                "/help - Get help"
    )
    @staticmethod
    def greet(self, username):
        return (
            f"👋 Welcome back {username}!\n\n"
                "Use /help to see available commands."
    )

