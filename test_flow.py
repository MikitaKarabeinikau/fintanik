# Test to understand the flow
from utils.config import Settings
emoji = Settings.emoji

print("Testing button texts:")
print(f"Update button: '{emoji('UPDATE')} Update Transaction'")
print(f"Expected match: text == '{emoji('UPDATE')} Update Transaction'")
print()
print("Flow:")
print("1. User in SPENDINGS menu")
print("2. Clicks '✏️ Update Transaction'")
print("3. handle_spendings_menu() sets date_range_updating=True")
print("4. Shows dates menu")
print("5. User clicks 'TODAY'")
print("6. handle_main_menu_button() receives 'TODAY'")
print("7. Checks date_range_updating flag -> calls handle_transaction_range()")
