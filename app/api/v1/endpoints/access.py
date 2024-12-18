from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from fastapi.responses import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import tempfile
from app.api import deps
from app.models.user import User
from app.models.access_log import AccessLog
from app.schemas import access_log as access_schemas

router = APIRouter()


@router.post("/record", response_model=access_schemas.AccessLog)
def record_access(
        *,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user),
        access_data: access_schemas.AccessLogCreate
) -> Any:
    """
    Registrar una entrada o salida del usuario actual
    """
    # Verificar tipo de acceso válido
    if access_data.access_type not in ["entry", "exit"]:
        raise HTTPException(
            status_code=400,
            detail="Tipo de acceso debe ser 'entry' o 'exit'"
        )

    # Crear registro de acceso
    access_log = AccessLog(
        user_id=current_user.id,
        access_type=access_data.access_type,
        status="success",
        device_id=access_data.device_id
    )

    db.add(access_log)
    db.commit()
    db.refresh(access_log)
    return access_log


@router.get("/history", response_model=List[access_schemas.AccessLog])
def get_access_history(
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user),
        skip: int = 0,
        limit: int = 100
) -> Any:
    """
    Obtener historial de accesos del usuario actual
    """
    access_logs = db.query(AccessLog) \
        .filter(AccessLog.user_id == current_user.id) \
        .order_by(AccessLog.timestamp.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()
    return access_logs


@router.get("/today", response_model=List[access_schemas.AccessLog])
def get_today_access(
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Obtener registros de acceso del día actual
    """
    today = datetime.now().date()
    access_logs = db.query(AccessLog) \
        .filter(
        AccessLog.user_id == current_user.id,
        AccessLog.timestamp >= today
    ) \
        .order_by(AccessLog.timestamp.desc()) \
        .all()
    return access_logs


@router.get("/admin/logs", response_model=List[access_schemas.AccessLogWithUser])
def get_all_access_logs(
        *,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        user_id: Optional[int] = Query(None),
        access_type: Optional[str] = Query(None),
        device_id: Optional[str] = Query(None),
        skip: int = 0,
        limit: int = 100
) -> Any:
    """
    Obtener todos los registros de acceso con filtros (solo admin)
    """
    query = db.query(AccessLog)

    if start_date:
        query = query.filter(func.date(AccessLog.timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(AccessLog.timestamp) <= end_date)
    if user_id:
        query = query.filter(AccessLog.user_id == user_id)
    if access_type:
        query = query.filter(AccessLog.access_type == access_type)
    if device_id:
        query = query.filter(AccessLog.device_id == device_id)

    return query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()


@router.get("/admin/stats/device", response_model=List[dict])
def get_device_stats(
        *,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None)
) -> Any:
    """
    Obtener estadísticas de uso por dispositivo
    """
    query = db.query(
        AccessLog.device_id,
        func.count(AccessLog.id).label('total_accesses'),
        func.count(func.distinct(AccessLog.user_id)).label('unique_users')
    )

    if start_date:
        query = query.filter(func.date(AccessLog.timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(AccessLog.timestamp) <= end_date)

    return query.group_by(AccessLog.device_id).all()


# Endpoint de exportación a PDF
@router.get("/admin/export-pdf")
def export_access_logs_pdf(
        *,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        user_id: Optional[int] = Query(None)
) -> Any:
    """Exportar registros de acceso a PDF"""
    # Obtener datos
    query = db.query(AccessLog).join(User)
    if start_date:
        query = query.filter(func.date(AccessLog.timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(AccessLog.timestamp) <= end_date)
    if user_id:
        query = query.filter(AccessLog.user_id == user_id)

    logs = query.order_by(AccessLog.timestamp.desc()).all()

    # Crear PDF temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=letter)
        elements = []

        # Crear tabla
        data = [['Fecha', 'Usuario', 'Tipo', 'Dispositivo', 'Estado']]
        for log in logs:
            data.append([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.user.full_name,
                log.access_type,
                log.device_id,
                log.status
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        doc.build(elements)

        return FileResponse(
            tmp.name,
            media_type='application/pdf',
            filename=f'access_logs_{datetime.now().strftime("%Y%m%d")}.pdf'
        )

@router.get("/history/filtered", response_model=List[access_schemas.AccessLog])
def get_filtered_access_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user_id: Optional[int] = Query(None),
    access_type: Optional[str] = Query(None),
    device_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """
    Obtener historial de accesos con filtros
    """
    query = db.query(AccessLog).join(User)

    if start_date:
        query = query.filter(func.date(AccessLog.timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(AccessLog.timestamp) <= end_date)
    if user_id:
        query = query.filter(AccessLog.user_id == user_id)
    if access_type:
        query = query.filter(AccessLog.access_type == access_type)
    if device_id:
        query = query.filter(AccessLog.device_id == device_id)
    if status:
        query = query.filter(AccessLog.status == status)

    return query.order_by(AccessLog.timestamp.desc()).all()
