"""
API Monitor CRUD endpoints.
Allows users to create, read, update, and delete API monitors.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.api_monitor import APIMonitor
from app.schemas.monitor import MonitorCreate, MonitorUpdate, MonitorResponse, MonitorListResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    monitor_data: MonitorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new API monitor.

    Requires authentication.

    Args:
        monitor_data: Monitor configuration
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created monitor data
    """
    # Create new monitor associated with current user
    new_monitor = APIMonitor(
        user_id=current_user.id,
        name=monitor_data.name,
        url=monitor_data.url,
        method=monitor_data.method,
        headers=monitor_data.headers or {},
        expected_status=monitor_data.expected_status,
        check_interval=monitor_data.check_interval,
        timeout=monitor_data.timeout,
        is_active=monitor_data.is_active
    )

    db.add(new_monitor)
    await db.commit()
    await db.refresh(new_monitor)

    return new_monitor


@router.get("/", response_model=MonitorListResponse)
async def list_monitors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all monitors for the current user.

    Requires authentication.

    Args:
        current_user: Current authenticated user
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of monitors and total count
    """
    # Get total count
    count_query = select(func.count()).select_from(APIMonitor).where(
        APIMonitor.user_id == current_user.id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get monitors
    query = select(APIMonitor).where(
        APIMonitor.user_id == current_user.id
    ).offset(skip).limit(limit).order_by(APIMonitor.created_at.desc())

    result = await db.execute(query)
    monitors = result.scalars().all()

    return {
        "total": total,
        "monitors": monitors
    }


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(
    monitor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific monitor by ID.

    Requires authentication. Users can only access their own monitors.

    Args:
        monitor_id: Monitor ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Monitor data

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


@router.put("/{monitor_id}", response_model=MonitorResponse)
async def update_monitor(
    monitor_id: int,
    monitor_data: MonitorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a monitor.

    Requires authentication. Users can only update their own monitors.

    Args:
        monitor_id: Monitor ID
        monitor_data: Updated monitor data (only provided fields will be updated)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated monitor data

    Raises:
        HTTPException: If monitor not found or access denied
    """
    # Get monitor
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

    # Update only provided fields
    update_data = monitor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(monitor, field, value)

    await db.commit()
    await db.refresh(monitor)

    return monitor


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(
    monitor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a monitor.

    Requires authentication. Users can only delete their own monitors.

    Args:
        monitor_id: Monitor ID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If monitor not found or access denied
    """
    # Get monitor
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

    # Delete monitor (cascade will delete related health checks and incidents)
    await db.delete(monitor)
    await db.commit()

    return None
