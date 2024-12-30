from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List

from app.api import deps
from app.models.user import User
from app.models.access_log import AccessLog

router = APIRouter()


@router.get("/daily")
async def get_daily_report(
        start_date: date = Query(None),
        end_date: date = Query(None),
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin)
):
    """
    Reporte diario de accesos
    """
    query = db.query(
        func.date(AccessLog.timestamp).label('date'),
        func.count().label('total_accesses'),
        func.count(func.distinct(AccessLog.user_id)).label('unique_users')
    )

    if start_date:
        query = query.filter(func.date(AccessLog.timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(AccessLog.timestamp) <= end_date)

    return query.group_by(func.date(AccessLog.timestamp)).all()


@router.get("/user-stats")
async def get_user_stats(
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin)
):
    """
    Estadísticas por usuario
    """
    return db.query(
        User.id,
        User.full_name,
        func.count(AccessLog.id).label('total_accesses'),
        func.min(AccessLog.timestamp).label('first_access'),
        func.max(AccessLog.timestamp).label('last_access')
    ).join(AccessLog).group_by(User.id).all()
