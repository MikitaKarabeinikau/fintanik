from database.credit.services import get_unpaid_credit_payments_dict
from telegram.ext import ContextTypes


def show_credit_flow_info(context: ContextTypes.DEFAULT_TYPE):
    message = (f'Credit/Loan Flow Info:\n'
               f'Amount: {context.user_data["credit_details"]["total_amount"]}\n'
               f'Category: {context.user_data["credit_details"]["category"]}\n'
               f'Lender: {context.user_data["credit_details"]["lender_name"]}\n'
               f'Start Date: {context.user_data["credit_details"]["start_date"]}\n'
               f'End Date: {context.user_data["credit_details"]["end_date"]}\n'
               f'Monthly Payment: {context.user_data["credit_details"]["monthly_payment"]}\n'
               f'Last Payment: {context.user_data["credit_details"]["last_payment"]}\n'
               )
    return message 



def show_credit_info():
    payments = get_unpaid_credit_payments_dict()
    
    if not payments:
        return "✅ No unpaid credit payments."
    
    # Limit to first 20 payments to avoid message length issues
    max_payments = 20
    payments_to_show = payments[:max_payments]
    
    # Column widths
    lender_w = 10
    category_w = 10
    amount_w = 9
    
    # Build message
    lines = ["📋 Nearest Unpaid Credit Payments\n"]
    lines.append(f"{'Lender':<{lender_w}} {'Category':<{category_w}} {'Amount':>{amount_w}} Date")
    lines.append("-" * 42)  # Fixed total width
    
    for payment in payments_to_show:
        lender = (payment['lender_name'] or 'N/A')[:lender_w]
        category = (payment['category'] or 'N/A')[:category_w]
        amount = payment['amount']
        payment_date = payment['payment_date'].strftime('%d.%m.%Y') if hasattr(payment['payment_date'], 'strftime') else str(payment['payment_date'])
        
        # Fixed: ensure date fits on same line, remove extra spaces
        lines.append(f"{lender:<{lender_w}} {category:<{category_w}} {amount:>6.2f} zl {payment_date}")
    
    lines.append("-" * 42)
    
    if len(payments) > max_payments:
        lines.append(f"\n... and {len(payments) - max_payments} more")
    else:
        lines.append(f"\n📊 Total: {len(payments)} unpaid payments")
    
    message = "\n".join(lines)
    
    # Safety check for message length
    if len(message) > 4000:
        message = message[:4000] + "\n... (truncated)"
    
    return message