

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.config import Settings

emoji = Settings.emoji

class ButtonBuilder:
    """Helper class for building dynamic keyboards"""
    
    @staticmethod
    def create_grid(items,  callback_prefix='item', emoji_map=None):
        """Create a grid of buttons"""
        keyboard = []
        
        for i, item in enumerate(items):
            emoji = emoji_map.get(item, '') if emoji_map else ''
            text = f"{emoji} {str(item).capitalize()}" if emoji else str(item).capitalize()
            callback = f'{callback_prefix}_{item}'
            
            keyboard.append(InlineKeyboardButton(text, callback_data=callback))
            
            
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def add_new_button(keyboard):
        """Add new button to keyboard"""
        keyboard.append([
            InlineKeyboardButton(f"{emoji('NEW')} New", callback_data='new')
        ])
        return keyboard

    @staticmethod
    def add_back_button(keyboard):
        """Add back button to keyboard"""
        keyboard.append([
            InlineKeyboardButton(f"{emoji('BACK')} Back", callback_data='back')
        ])
        return keyboard
    

    @staticmethod
    def add_cancel_button(keyboard):
        """Add cancel button to keyboard"""
        keyboard.append([
            InlineKeyboardButton(f"{emoji('CANCEL')} Cancel", callback_data='cancel')
        ])
        return keyboard
