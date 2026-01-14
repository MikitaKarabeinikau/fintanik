from datetime import datetime, time, timedelta
from telegram.ext import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database.user.crud import get_all_users
from database.transactions.services import get_transactions_by_date_range
from utils.utils import view_statistics_all
from utils.config import Settings
import logging

logger = Settings.LOGGER


async def send_daily_stats(app: Application):
    """Send daily statistics to all users at end of day"""
    logger.info("Starting daily stats job")
    users = get_all_users()
    
    today = datetime.now().date()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)
    
    for user in users:
        try:
            transactions = get_transactions_by_date_range(user.telegram_id, start, end)
            if transactions:
                message = view_statistics_all("📊 Daily Report - TODAY", transactions)
                await app.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"<pre>{message}</pre>",
                    parse_mode='HTML'
                )
                logger.info(f"Sent daily stats to user {user.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send daily stats to {user.telegram_id}: {e}")


async def send_weekly_stats(app: Application):
    """Send weekly statistics to all users at end of week"""
    logger.info("Starting weekly stats job")
    users = get_all_users()
    
    today = datetime.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    start = datetime.combine(start_of_week, time.min)
    end = datetime.combine(today, time.max)
    
    for user in users:
        try:
            transactions = get_transactions_by_date_range(user.telegram_id, start, end)
            if transactions:
                message = view_statistics_all("📊 Weekly Report - THIS WEEK", transactions)
                await app.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"<pre>{message}</pre>",
                    parse_mode='HTML'
                )
                logger.info(f"Sent weekly stats to user {user.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send weekly stats to {user.telegram_id}: {e}")


async def send_monthly_stats(app: Application):
    """Send monthly statistics to all users at end of month"""
    logger.info("Starting monthly stats job")
    users = get_all_users()
    
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    start = datetime.combine(start_of_month, time.min)
    end = datetime.combine(today, time.max)
    
    for user in users:
        try:
            transactions = get_transactions_by_date_range(user.telegram_id, start, end)
            if transactions:
                message = view_statistics_all("📊 Monthly Report - THIS MONTH", transactions)
                await app.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"<pre>{message}</pre>",
                    parse_mode='HTML'
                )
                logger.info(f"Sent monthly stats to user {user.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send monthly stats to {user.telegram_id}: {e}")


async def send_yearly_stats(app: Application):
    """Send yearly statistics to all users at end of year"""
    logger.info("Starting yearly stats job")
    users = get_all_users()
    
    today = datetime.now().date()
    start_of_year = today.replace(month=1, day=1)
    start = datetime.combine(start_of_year, time.min)
    end = datetime.combine(today, time.max)
    
    for user in users:
        try:
            transactions = get_transactions_by_date_range(user.telegram_id, start, end)
            if transactions:
                message = view_statistics_all("📊 Yearly Report - THIS YEAR", transactions)
                await app.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"<pre>{message}</pre>",
                    parse_mode='HTML'
                )
                logger.info(f"Sent yearly stats to user {user.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send yearly stats to {user.telegram_id}: {e}")


def setup_scheduler(app: Application):
    """Set up scheduled jobs"""
    scheduler = AsyncIOScheduler()
    
    # Daily stats at 23:55 every day
    scheduler.add_job(
        send_daily_stats,
        CronTrigger(hour=23, minute=55),
        args=[app],
        id='daily_stats',
        name='Send daily statistics'
    )
    
    # Weekly stats on Sunday at 23:55
    scheduler.add_job(
        send_weekly_stats,
        CronTrigger(day_of_week='sun', hour=23, minute=55),
        args=[app],
        id='weekly_stats',
        name='Send weekly statistics'
    )
    
    # Monthly stats on last day of month at 23:55
    scheduler.add_job(
        send_monthly_stats,
        CronTrigger(day='last', hour=23, minute=55),
        args=[app],
        id='monthly_stats',
        name='Send monthly statistics'
    )
    
    # Yearly stats on December 31st at 23:55
    scheduler.add_job(
        send_yearly_stats,
        CronTrigger(month=12, day=31, hour=23, minute=55),
        args=[app],
        id='yearly_stats',
        name='Send yearly statistics'
    )
    
    scheduler.start()
    logger.info("Scheduler started with all jobs")
    
    return scheduler