"""
APScheduler setup for running background health checks.
"""
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.workers.health_checker import check_all_active_monitors

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: AsyncIOScheduler = None


def start_scheduler():
    """
    Start the background scheduler for health checks.

    Runs health checks every 60 seconds for all active monitors.
    """
    global scheduler

    if scheduler is not None:
        logger.warning("Scheduler already running")
        return

    logger.info("🚀 Starting health check scheduler...")

    # Create scheduler
    scheduler = AsyncIOScheduler()

    # Add health check job (runs every 60 seconds)
    scheduler.add_job(
        func=check_all_active_monitors,
        trigger=IntervalTrigger(seconds=60),  # Check every minute
        id="health_check_job",
        name="Check all active monitors",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
        misfire_grace_time=30  # Allow 30s grace period for missed runs
    )

    # Start scheduler
    scheduler.start()

    logger.info("✅ Scheduler started - Health checks will run every 60 seconds")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler

    if scheduler is None:
        return

    logger.info("🛑 Stopping health check scheduler...")

    scheduler.shutdown(wait=True)
    scheduler = None

    logger.info("✅ Scheduler stopped")


def get_scheduler() -> AsyncIOScheduler:
    """Get the global scheduler instance."""
    return scheduler
