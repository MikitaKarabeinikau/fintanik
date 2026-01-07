from database.budget.crud import get_all_budgets_for_current_month
from database.transactions.services import get_grouped_spendings_by_category_for_current_month
from utils.config import Settings


def get_difference_between_budgets_and_spendings():
    budgets = get_all_budgets_for_current_month()
    spendings = get_grouped_spendings_by_category_for_current_month()

    not_in_budget = set(spendings.keys()) - set(budgets.keys())

    
    difference_dict = {}
    for category, budget_amount in budgets.items():
        print(f"💰 BUDGET SERVICE: Processing category '{category}' with budget {budget_amount}")
        spending_amount = spendings.get(category, 0)
        difference = budget_amount - spending_amount
        difference_dict[category] = difference
    
    for category in not_in_budget:
        spending_amount = spendings[category]
        difference_dict[category] = -spending_amount  # Overspent since no budget set

    unsetted_default_categories = set(Settings.CATEGORIES) - set(difference_dict.keys()) 
    for category in unsetted_default_categories:
        difference_dict[category] = 0  # No budget and no spendings
    print(f"💰 BUDGET SERVICE: Difference between budgets and spendings: {difference_dict}")
    return difference_dict

def get_unset_budgets_categories():
    budgets = get_all_budgets_for_current_month()
    default_categories = set(Settings.CATEGORIES)
    budgeted_categories = set(budgets.keys())
    unset_categories = default_categories - budgeted_categories
    return unset_categories