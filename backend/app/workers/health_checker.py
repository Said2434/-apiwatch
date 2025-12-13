"""
Background health checker worker.
Periodically checks monitored APIs and stores results.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.api_monitor import APIMonitor
from app.models.health_check import HealthCheck
from app.models.incident import Incident

logger = logging.getLogger(__name__)


class HealthCheckExecutor:
    """Executes health checks for API monitors."""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,  # Max timeout for any request
            follow_redirects=True
        )

    async def check_api(self, monitor: APIMonitor) -> dict:
        """
        Perform a health check on a single API monitor.

        Args:
            monitor: APIMonitor instance to check

        Returns:
            dict with check results (status_code, response_time, is_up, error_message)
        """
        start_time = datetime.utcnow()
        result = {
            "status_code": None,
            "response_time": None,
            "is_up": False,
            "error_message": None
        }

        try:
            # Prepare request
            headers = monitor.headers or {}
            timeout = httpx.Timeout(monitor.timeout, connect=5.0)

            # Make HTTP request
            response = await self.client.request(
                method=monitor.method.value,
                url=monitor.url,
                headers=headers,
                timeout=timeout
            )

            # Calculate response time in milliseconds
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            # Check if response matches expected status
            result["status_code"] = response.status_code
            result["response_time"] = round(response_time_ms, 2)
            result["is_up"] = response.status_code == monitor.expected_status

            if not result["is_up"]:
                result["error_message"] = (
                    f"Expected status {monitor.expected_status}, "
                    f"got {response.status_code}"
                )

            logger.info(
                f"Health check for '{monitor.name}': "
                f"status={response.status_code}, "
                f"time={result['response_time']}ms, "
                f"is_up={result['is_up']}"
            )

        except httpx.TimeoutException:
            result["error_message"] = f"Request timeout after {monitor.timeout}s"
            logger.warning(f"Health check timeout for '{monitor.name}': {monitor.url}")

        except httpx.NetworkError as e:
            result["error_message"] = f"Network error: {str(e)}"
            logger.warning(f"Network error for '{monitor.name}': {str(e)}")

        except Exception as e:
            result["error_message"] = f"Unexpected error: {str(e)}"
            logger.error(f"Error checking '{monitor.name}': {str(e)}")

        return result

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def save_health_check(
    db: AsyncSession,
    monitor_id: int,
    result: dict
) -> HealthCheck:
    """
    Save health check result to database.

    Args:
        db: Database session
        monitor_id: ID of the monitor
        result: Health check result dictionary

    Returns:
        Created HealthCheck instance
    """
    health_check = HealthCheck(
        monitor_id=monitor_id,
        status_code=result["status_code"],
        response_time=result["response_time"],
        is_up=result["is_up"],
        error_message=result["error_message"]
    )

    db.add(health_check)
    await db.commit()
    await db.refresh(health_check)

    return health_check


async def handle_incident(
    db: AsyncSession,
    monitor: APIMonitor,
    is_up: bool
) -> Optional[Incident]:
    """
    Handle incident creation and resolution.

    Creates incident when API goes down.
    Resolves incident when API comes back up.

    Args:
        db: Database session
        monitor: APIMonitor instance
        is_up: Whether the current check passed

    Returns:
        Incident instance if created/updated, None otherwise
    """
    # Get latest ongoing incident for this monitor
    query = select(Incident).where(
        Incident.monitor_id == monitor.id,
        Incident.resolved_at.is_(None)
    ).order_by(Incident.started_at.desc())

    result = await db.execute(query)
    ongoing_incident = result.scalar_one_or_none()

    if not is_up:
        # API is down
        if not ongoing_incident:
            # Create new incident
            incident = Incident(
                monitor_id=monitor.id,
                alert_sent=False  # Will implement alerts later
            )
            db.add(incident)
            await db.commit()
            await db.refresh(incident)

            logger.warning(
                f"🚨 INCIDENT CREATED: '{monitor.name}' is DOWN! "
                f"Incident ID: {incident.id}"
            )

            return incident

    else:
        # API is up
        if ongoing_incident:
            # Resolve the incident
            now = datetime.utcnow()
            ongoing_incident.resolved_at = now
            duration = (now - ongoing_incident.started_at).total_seconds()
            ongoing_incident.duration = int(duration)

            await db.commit()
            await db.refresh(ongoing_incident)

            logger.info(
                f"✅ INCIDENT RESOLVED: '{monitor.name}' is back UP! "
                f"Downtime: {duration:.0f}s"
            )

            return ongoing_incident

    return None


async def perform_health_check(monitor: APIMonitor):
    """
    Complete health check workflow for a single monitor.

    1. Execute health check
    2. Save result to database
    3. Handle incident detection/resolution

    Args:
        monitor: APIMonitor to check
    """
    executor = HealthCheckExecutor()

    try:
        # Execute health check
        result = await executor.check_api(monitor)

        # Save to database
        async with AsyncSessionLocal() as db:
            # Save health check result
            await save_health_check(db, monitor.id, result)

            # Handle incidents
            await handle_incident(db, monitor, result["is_up"])

    except Exception as e:
        logger.error(f"Error in health check workflow for '{monitor.name}': {str(e)}")

    finally:
        await executor.close()


async def check_all_active_monitors():
    """
    Check all active monitors.
    Called periodically by APScheduler.
    """
    logger.info("🔍 Starting health check cycle for all active monitors...")

    async with AsyncSessionLocal() as db:
        # Get all active monitors
        query = select(APIMonitor).where(APIMonitor.is_active == True)
        result = await db.execute(query)
        monitors = result.scalars().all()

        if not monitors:
            logger.info("No active monitors found")
            return

        logger.info(f"Found {len(monitors)} active monitor(s)")

        # Check all monitors concurrently
        tasks = [perform_health_check(monitor) for monitor in monitors]
        await asyncio.gather(*tasks, return_exceptions=True)

    logger.info("✅ Health check cycle complete")
