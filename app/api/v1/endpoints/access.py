from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
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
import logging

logger = logging.getLogger(__name__)
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


@router.get("/admin/check-records")
def check_access_logs_exist(
        *,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        employee_id: Optional[str] = Query(None),
        full_name: Optional[str] = Query(None)
) -> dict:
    """Verificar si existen registros de acceso con los filtros especificados"""
    query = db.query(func.count(AccessLog.id)).join(User)

    if start_date:
        query = query.filter(func.date(AccessLog.timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(AccessLog.timestamp) <= end_date)
    if employee_id:
        query = query.filter(User.employee_id == employee_id)
    if full_name:
        query = query.filter(User.full_name.ilike(f"%{full_name}%"))

    count = query.scalar()

    return {
        "hasRecords": count > 0,
        "count": count
    }


# Endpoint de exportación a PDF
@router.get("/admin/export-pdf")
def export_access_logs_pdf(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[str] = Query(None),  # Cambiado de user_id
    full_name: Optional[str] = Query(None)     # Nuevo
) -> Any:
    """Exportar registros de acceso a PDF"""
    query = db.query(AccessLog).join(User)

    if start_date:
        query = query.filter(func.date(AccessLog.timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(AccessLog.timestamp) <= end_date)
    if employee_id:
        query = query.filter(User.employee_id == employee_id)
    if full_name:
        query = query.filter(User.full_name.ilike(f"%{full_name}%"))

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


@router.get("/history/filtered", response_model=List[access_schemas.AccessLogWithUser])
def get_filtered_access_history(
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        employee_id: Optional[str] = Query(None),  # Cambiado a str
        email: Optional[str] = Query(None),
        full_name: Optional[str] = Query(None),
        access_type: Optional[str] = Query(None),
        device_id: Optional[str] = Query(None),
        status: Optional[str] = Query(None)
):
    """
    Obtener historial de accesos con filtros
    """
    try:
        logger.info(f"Iniciando búsqueda con filtros: {locals()}")

        # Construir la consulta base
        query = db.query(AccessLog)

        # Aplicar los filtros
        if start_date:
            query = query.filter(func.date(AccessLog.timestamp) >= start_date)
        if end_date:
            query = query.filter(func.date(AccessLog.timestamp) <= end_date)
        if employee_id:
            query = query.join(User).filter(User.employee_id == employee_id)
        if email:
            query = query.join(User).filter(User.email.ilike(f"%{email}%"))
        if full_name:
            query = query.join(User).filter(User.full_name.ilike(f"%{full_name}%"))
        if access_type:
            query = query.filter(AccessLog.access_type == access_type)
        if device_id:
            query = query.filter(AccessLog.device_id == device_id)
        if status:
            query = query.filter(AccessLog.status == status)

        # Asegurarnos de que la relación user está cargada
        if not any([employee_id, email, full_name]):
            query = query.join(User)

        result = query.order_by(AccessLog.timestamp.desc()).all()
        logger.info(f"Búsqueda completada. Encontrados {len(result)} registros")

        return result
    except Exception as e:
        logger.error(f"Error en get_filtered_access_history: {str(e)}")
        logger.exception("Traceback completo:")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )