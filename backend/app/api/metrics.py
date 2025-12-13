"""
Metrics and statistics API endpoints.
View health check history, uptime stats, and incidents.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.api_monitor import APIMonitor
from app.models.health_check import HealthCheck
from app.models.incident import Incident
from app.schemas.metrics import (
    HealthCheckResponse,
    HealthCheckListResponse,
    IncidentResponse,
    IncidentListResponse,
    MonitorStats,
    DashboardStats
)
from app.api.auth import get_current_user

router = APIRouter()


async def verify_monitor_access(
    monitor_id: int,
    current_user: User,
    db: AsyncSession
) -> APIMonitor:
    """
    Verify user has access to the monitor.

    Args:
        monitor_id: Monitor ID
        current_user: Current user
        db: Database session

    Returns:
        Monitor if found and user has access

    Raises:
        HTTPException: If monitor not found or access denied
    """
    query = select(APIMonitor).where(
        APIMonitor.id == monitor_id,
        APIMonitor.user_id == current_user.id
    )
    result = await db.execute(query)
    monitor = result.scalar_one_or_none()

    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found"
        )

    return monitor


@router.get("/{monitor_id}/health-checks", response_model=HealthCheckListResponse)
async def get_health_checks(
    monitor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    hours: Optional[int] = Query(None, description="Filter by last N hours")
):
    """
    Get health check history for a monitor.

    Args:
        monitor_id: Monitor ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        hours: Optional filter for last N hours

    Returns:
        List of health checks with pagination
    """
    # Verify access
    await verify_monitor_access(monitor_id, current_user, db)

    # Build query
    query = select(HealthCheck).where(HealthCheck.monitor_id == monitor_id)

    # Filter by time if specified
    if hours:
        since = datetime.utcnow() - timedelta(hours=hours)
        query = query.where(HealthCheck.checked_at >= since)

    # Get total count
    count_query = select(func.count()).select_from(HealthCheck).where(
        HealthCheck.monitor_id == monitor_id
    )
    if hours:
        count_query = count_query.where(HealthCheck.checked_at >= since)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get health checks (most recent first)
    query = query.order_by(HealthCheck.checked_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    health_checks = result.scalars().all()

    return {
        "total": total,
        "health_checks": health_checks
    }


@router.get("/{monitor_id}/stats", response_model=MonitorStats)
async def get_monitor_stats(
    monitor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    hours: Optional[int] = Query(24, description="Calculate stats for last N hours")
):
    """
    Get statistics for a monitor.

    Calculates:
    - Total checks
    - Successful/failed checks
    - Uptime percentage
    - Average response time
    - Incident count

    Args:
        monitor_id: Monitor ID
        hours: Calculate stats for last N hours (default: 24)

    Returns:
        Monitor statistics
    """
    # Verify access
    monitor = await verify_monitor_access(monitor_id, current_user, db)

    # Time filter
    since = datetime.utcnow() - timedelta(hours=hours) if hours else None

    # Get total checks
    checks_query = select(func.count()).select_from(HealthCheck).where(
        HealthCheck.monitor_id == monitor_id
    )
    if since:
        checks_query = checks_query.where(HealthCheck.checked_at >= since)

    total_result = await db.execute(checks_query)
    total_checks = total_result.scalar() or 0

    # Get successful checks
    success_query = select(func.count()).select_from(HealthCheck).where(
        HealthCheck.monitor_id == monitor_id,
        HealthCheck.is_up == True
    )
    if since:
        success_query = success_query.where(HealthCheck.checked_at >= since)

    success_result = await db.execute(success_query)
    successful_checks = success_result.scalar() or 0

    # Calculate uptime percentage
    failed_checks = total_checks - successful_checks
    uptime_percentage = (successful_checks / total_checks * 100) if total_checks > 0 else 100.0

    # Get average response time (only for successful checks)
    avg_query = select(func.avg(HealthCheck.response_time)).where(
        HealthCheck.monitor_id == monitor_id,
        HealthCheck.is_up == True,
        HealthCheck.response_time.isnot(None)
    )
    if since:
        avg_query = avg_query.where(HealthCheck.checked_at >= since)

    avg_result = await db.execute(avg_query)
    avg_response_time = avg_result.scalar()

    # Get last check
    last_check_query = select(HealthCheck).where(
        HealthCheck.monitor_id == monitor_id
    ).order_by(HealthCheck.checked_at.desc()).limit(1)

    last_check_result = await db.execute(last_check_query)
    last_check = last_check_result.scalar_one_or_none()

    # Get incident counts
    total_incidents_query = select(func.count()).select_from(Incident).where(
        Incident.monitor_id == monitor_id
    )
    total_incidents_result = await db.execute(total_incidents_query)
    total_incidents = total_incidents_result.scalar() or 0

    ongoing_incidents_query = select(func.count()).select_from(Incident).where(
        Incident.monitor_id == monitor_id,
        Incident.resolved_at.is_(None)
    )
    ongoing_incidents_result = await db.execute(ongoing_incidents_query)
    ongoing_incidents = ongoing_incidents_result.scalar() or 0

    return MonitorStats(
        monitor_id=monitor.id,
        monitor_name=monitor.name,
        total_checks=total_checks,
        successful_checks=successful_checks,
        failed_checks=failed_checks,
        uptime_percentage=round(uptime_percentage, 2),
        avg_response_time=round(avg_response_time, 2) if avg_response_time else None,
        last_check_at=last_check.checked_at if last_check else None,
        last_check_status=last_check.is_up if last_check else None,
        total_incidents=total_incidents,
        ongoing_incidents=ongoing_incidents
    )


@router.get("/{monitor_id}/incidents", response_model=IncidentListResponse)
async def get_incidents(
    monitor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    ongoing_only: bool = Query(False, description="Show only ongoing incidents")
):
    """
    Get incident history for a monitor.

    Args:
        monitor_id: Monitor ID
        skip: Number of records to skip
        limit: Maximum number of records
        ongoing_only: Filter to show only ongoing incidents

    Returns:
        List of incidents with pagination
    """
    # Verify access
    await verify_monitor_access(monitor_id, current_user, db)

    # Build query
    query = select(Incident).where(Incident.monitor_id == monitor_id)

    if ongoing_only:
        query = query.where(Incident.resolved_at.is_(None))

    # Get total count
    count_query = select(func.count()).select_from(Incident).where(
        Incident.monitor_id == monitor_id
    )
    if ongoing_only:
        count_query = count_query.where(Incident.resolved_at.is_(None))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get incidents (most recent first)
    query = query.order_by(Incident.started_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    incidents = result.scalars().all()

    return {
        "total": total,
        "incidents": incidents
    }


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    hours: int = Query(24, description="Calculate stats for last N hours")
):
    """
    Get overall dashboard statistics for all user's monitors.

    Returns:
        Dashboard statistics with all monitors
    """
    # Get all user's monitors
    monitors_query = select(APIMonitor).where(APIMonitor.user_id == current_user.id)
    monitors_result = await db.execute(monitors_query)
    monitors = monitors_result.scalars().all()

    total_monitors = len(monitors)
    active_monitors = sum(1 for m in monitors if m.is_active)
    inactive_monitors = total_monitors - active_monitors

    # Get overall incident counts
    total_incidents_query = select(func.count()).select_from(Incident).join(
        APIMonitor
    ).where(APIMonitor.user_id == current_user.id)

    total_incidents_result = await db.execute(total_incidents_query)
    total_incidents = total_incidents_result.scalar() or 0

    ongoing_incidents_query = select(func.count()).select_from(Incident).join(
        APIMonitor
    ).where(
        APIMonitor.user_id == current_user.id,
        Incident.resolved_at.is_(None)
    )

    ongoing_incidents_result = await db.execute(ongoing_incidents_query)
    ongoing_incidents = ongoing_incidents_result.scalar() or 0

    # Get stats for each monitor
    monitor_stats = []
    total_uptime_sum = 0

    for monitor in monitors:
        # Get stats for this monitor (reuse logic from get_monitor_stats)
        since = datetime.utcnow() - timedelta(hours=hours)

        # Total checks
        checks_query = select(func.count()).select_from(HealthCheck).where(
            HealthCheck.monitor_id == monitor.id,
            HealthCheck.checked_at >= since
        )
        total_checks = (await db.execute(checks_query)).scalar() or 0

        # Successful checks
        success_query = select(func.count()).select_from(HealthCheck).where(
            HealthCheck.monitor_id == monitor.id,
            HealthCheck.is_up == True,
            HealthCheck.checked_at >= since
        )
        successful_checks = (await db.execute(success_query)).scalar() or 0

        failed_checks = total_checks - successful_checks
        uptime_pct = (successful_checks / total_checks * 100) if total_checks > 0 else 100.0

        # Average response time
        avg_query = select(func.avg(HealthCheck.response_time)).where(
            HealthCheck.monitor_id == monitor.id,
            HealthCheck.is_up == True,
            HealthCheck.response_time.isnot(None),
            HealthCheck.checked_at >= since
        )
        avg_response_time = (await db.execute(avg_query)).scalar()

        # Last check
        last_check_query = select(HealthCheck).where(
            HealthCheck.monitor_id == monitor.id
        ).order_by(HealthCheck.checked_at.desc()).limit(1)
        last_check = (await db.execute(last_check_query)).scalar_one_or_none()

        # Incidents
        mon_incidents = (await db.execute(
            select(func.count()).select_from(Incident).where(Incident.monitor_id == monitor.id)
        )).scalar() or 0

        mon_ongoing = (await db.execute(
            select(func.count()).select_from(Incident).where(
                Incident.monitor_id == monitor.id,
                Incident.resolved_at.is_(None)
            )
        )).scalar() or 0

        monitor_stats.append(MonitorStats(
            monitor_id=monitor.id,
            monitor_name=monitor.name,
            total_checks=total_checks,
            successful_checks=successful_checks,
            failed_checks=failed_checks,
            uptime_percentage=round(uptime_pct, 2),
            avg_response_time=round(avg_response_time, 2) if avg_response_time else None,
            last_check_at=last_check.checked_at if last_check else None,
            last_check_status=last_check.is_up if last_check else None,
            total_incidents=mon_incidents,
            ongoing_incidents=mon_ongoing
        ))

        total_uptime_sum += uptime_pct

    # Calculate overall uptime
    overall_uptime = (total_uptime_sum / total_monitors) if total_monitors > 0 else 100.0

    return DashboardStats(
        total_monitors=total_monitors,
        active_monitors=active_monitors,
        inactive_monitors=inactive_monitors,
        total_incidents=total_incidents,
        ongoing_incidents=ongoing_incidents,
        overall_uptime=round(overall_uptime, 2),
        monitors=monitor_stats
    )
