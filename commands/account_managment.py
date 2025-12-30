import logging
import secrets
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from database.models import User, Account, Invitation, account_members
from utils.decorators import is_authenticated
from sqlalchemy import select

logger = logging.getLogger(__name__)

WAITING_ACCOUNT_NAME = 1


@is_authenticated
async def create_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start account creation"""
    await update.message.reply_text(
        "📊 *Create Shared Account*\n\n"
        "Choose a name for your shared account:\n"
        "(e.g., 'Family Budget', 'Roommates', 'Trip to Paris')",
        parse_mode='Markdown'
    )
    return WAITING_ACCOUNT_NAME


async def receive_account_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create account with given name"""
    user = update.effective_user
    account_name = update.message.text.strip()
    
    if len(account_name) < 2:
        await update.message.reply_text(
            "❌ Name too short. Please enter a valid account name:"
        )
        return WAITING_ACCOUNT_NAME
    
    session = db.get_session()
    try:
        # Get user from database
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        if not db_user:
            await update.message.reply_text("❌ User not found. Please /start first.")
            return ConversationHandler.END
        
        # Create account
        new_account = Account(
            name=account_name,
            owner_id=db_user.id
        )
        session.add(new_account)
        session.flush()  # Get the account ID
        
        # Add creator as member with 'owner' role
        stmt = account_members.insert().values(
            account_id=new_account.id,
            user_id=db_user.id,
            role='owner'
        )
        session.execute(stmt)
        session.commit()
        
        await update.message.reply_text(
            f"✅ Account '{account_name}' created!\n\n"
            f"Use /invite to invite others to join this account.\n"
            f"Use /accounts to see all your accounts."
        )
        
        logger.info(f"User {user.id} created account '{account_name}'")
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        session.rollback()
        await update.message.reply_text("❌ Error creating account.")
    finally:
        session.close()
    
    return ConversationHandler.END


@is_authenticated
async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all accounts user has access to"""
    user = update.effective_user
    session = db.get_session()
    
    try:
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        if not db_user:
            await update.message.reply_text("❌ User not found.")
            return
        
        accounts = db_user.accounts
        
        if not accounts:
            await update.message.reply_text(
                "📊 You don't have any accounts yet.\n\n"
                "Use /createaccount to create one!"
            )
            return
        
        keyboard = []
        text = "📊 *Your Accounts:*\n\n"
        
        for account in accounts:
            # Get role
            stmt = select(account_members.c.role).where(
                account_members.c.account_id == account.id,
                account_members.c.user_id == db_user.id
            )
            role = session.execute(stmt).scalar()
            
            # Count members
            member_count = len(account.members)
            
            text += f"• *{account.name}*\n"
            text += f"  Role: {role.capitalize()}\n"
            text += f"  Members: {member_count}\n\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"📊 {account.name}",
                    callback_data=f'account_select_{account.id}'
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("➕ Create New Account", callback_data='account_create')
        ])
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    finally:
        session.close()


@is_authenticated
async def invite_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate invite link"""
    user = update.effective_user
    session = db.get_session()
    
    try:
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        if not db_user:
            await update.message.reply_text("❌ User not found.")
            return
        
        # Get user's accounts where they are owner
        accounts = [acc for acc in db_user.accounts if acc.owner_id == db_user.id]
        
        if not accounts:
            await update.message.reply_text(
                "❌ You don't own any accounts.\n"
                "Use /createaccount to create one first!"
            )
            return
        
        # Show account selection
        keyboard = []
        for account in accounts:
            keyboard.append([
                InlineKeyboardButton(
                    account.name,
                    callback_data=f'invite_account_{account.id}'
                )
            ])
        
        await update.message.reply_text(
            "🔗 *Generate Invite Link*\n\n"
            "Select an account to invite someone:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    finally:
        session.close()


async def handle_invite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate invite code for selected account"""
    query = update.callback_query
    await query.answer()
    
    account_id = int(query.data.replace('invite_account_', ''))
    user = query.from_user
    
    session = db.get_session()
    try:
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        account = session.query(Account).get(account_id)
        
        if not account or account.owner_id != db_user.id:
            await query.edit_message_text("❌ Account not found or access denied.")
            return
        
        # Generate unique invite code
        invite_code = secrets.token_urlsafe(8)
        
        # Create invitation
        invitation = Invitation(
            account_id=account.id,
            invited_by=db_user.id,
            invite_code=invite_code,
            expires_at=datetime.utcnow() + timedelta(days=7)  # Expires in 7 days
        )
        session.add(invitation)
        session.commit()
        
        bot_username = context.bot.username
        invite_link = f"https://t.me/{bot_username}?start=join_{invite_code}"
        
        await query.edit_message_text(
            f"🔗 *Invite Link Generated!*\n\n"
            f"Account: *{account.name}*\n"
            f"Code: `{invite_code}`\n\n"
            f"Share this link:\n"
            f"{invite_link}\n\n"
            f"⏰ Expires in 7 days",
            parse_mode='Markdown'
        )
        
        logger.info(f"User {user.id} generated invite for account {account.id}")
    except Exception as e:
        logger.error(f"Error generating invite: {e}")
        await query.edit_message_text("❌ Error generating invite.")
    finally:
        session.close()


@is_authenticated
async def join_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Join account with invite code"""
    user = update.effective_user
    
    # Check if started with invite code
    if context.args and context.args[0].startswith('join_'):
        invite_code = context.args[0].replace('join_', '')
    else:
        await update.message.reply_text(
            "🔗 *Join Shared Account*\n\n"
            "Please enter the invite code:",
            parse_mode='Markdown'
        )
        return
    
    session = db.get_session()
    try:
        # Find invitation
        invitation = session.query(Invitation).filter_by(
            invite_code=invite_code,
            used=False
        ).first()
        
        if not invitation:
            await update.message.reply_text("❌ Invalid or expired invite code.")
            return
        
        if invitation.expires_at < datetime.utcnow():
            await update.message.reply_text("❌ Invite code expired.")
            return
        
        # Get user and account
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        account = session.query(Account).get(invitation.account_id)
        
        if not db_user or not account:
            await update.message.reply_text("❌ Error joining account.")
            return
        
        # Check if already member
        if db_user in account.members:
            await update.message.reply_text(
                f"ℹ️ You're already a member of '{account.name}'!"
            )
            return
        
        # Add user to account
        stmt = account_members.insert().values(
            account_id=account.id,
            user_id=db_user.id,
            role='member'
        )
        session.execute(stmt)
        
        # Mark invitation as used
        invitation.used = True
        session.commit()
        
        await update.message.reply_text(
            f"✅ Successfully joined account:\n"
            f"*{account.name}*\n\n"
            f"You can now add transactions to this account!",
            parse_mode='Markdown'
        )
        
        logger.info(f"User {user.id} joined account {account.id}")
    except Exception as e:
        logger.error(f"Error joining account: {e}")
        await update.message.reply_text("❌ Error joining account.")
    finally:
        session.close()


@is_authenticated
async def leave_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Leave a shared account"""
    user = update.effective_user
    session = db.get_session()
    
    try:
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        accounts = [acc for acc in db_user.accounts if acc.owner_id != db_user.id]
        
        if not accounts:
            await update.message.reply_text(
                "ℹ️ You're not a member of any accounts you can leave.\n"
                "(You can't leave accounts you own)"
            )
            return
        
        keyboard = []
        for account in accounts:
            keyboard.append([
                InlineKeyboardButton(
                    f"Leave '{account.name}'",
                    callback_data=f'leave_account_{account.id}'
                )
            ])
        
        await update.message.reply_text(
            "Select an account to leave:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    finally:
        session.close()


async def handle_leave_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle leaving an account"""
    query = update.callback_query
    await query.answer()
    
    account_id = int(query.data.replace('leave_account_', ''))
    user = query.from_user
    
    session = db.get_session()
    try:
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        account = session.query(Account).get(account_id)
        
        if not account or db_user not in account.members:
            await query.edit_message_text("❌ Account not found.")
            return
        
        # Remove from account
        stmt = account_members.delete().where(
            account_members.c.account_id == account.id,
            account_members.c.user_id == db_user.id
        )
        session.execute(stmt)
        session.commit()
        
        await query.edit_message_text(
            f"✅ You've left '{account.name}'"
        )
        
        logger.info(f"User {user.id} left account {account.id}")
    except Exception as e:
        logger.error(f"Error leaving account: {e}")
        await query.edit_message_text("❌ Error leaving account.")
    finally:
        session.close()