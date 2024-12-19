from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.core.security import decrypt_fingerprint, encrypt_fingerprint
from app.services.fingerprint_service import FingerprintService
from app.models.user import User
from app.models.access_log import AccessLog
from app.schemas import user as user_schemas
from datetime import datetime

router = APIRouter()
fingerprint_service = FingerprintService()


@router.post("/users/{user_id}/fingerprint", response_model=user_schemas.User)
async def register_fingerprint(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin)
):
    """Registrar huella de un usuario (solo admin)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        template = await fingerprint_service.register_fingerprint(db, user_id)
        if not template:
            raise HTTPException(status_code=400, detail="Error al registrar huella")

        # Encriptar y guardar template
        encrypted_template = encrypt_fingerprint(template)
        user.fingerprint_template = encrypted_template
        db.commit()
        db.refresh(user)
        print( "Huella registrada exitosamente")

        return user

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el registro de huella: {str(e)}")


@router.post("/verify")
async def verify_fingerprint(
        db: Session = Depends(deps.get_db)
):
    """Verificar huella y registrar acceso"""
    try:
        template = await fingerprint_service.capture_current_fingerprint()
        result = await fingerprint_service.verify_fingerprint(db, template)

        if result.get("is_valid"):
            # Registrar acceso
            access_log = AccessLog(
                user_id=result["user_id"],
                access_type=result["access_type"],
                status="success",
                timestamp=datetime.now()
            )
            db.add(access_log)
            db.commit()

            return {
                "status": "success",
                "user_id": result["user_id"],
                "access_type": result["access_type"]
            }

        raise HTTPException(status_code=401, detail="Huella no reconocida")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-false/{user_id}")
async def verify_fingerprint_false(
        user_id: int,
        db: Session = Depends(deps.get_db),
):
    """Verificar huella contra una incorrecta (para pruebas)"""
    is_valid = await fingerprint_service.verify_fingerprint_false(db, user_id)
    return {
        "is_valid": is_valid,
        "message": "Verificación fallida - Huella no coincide"
    }


# Versión para cuando se tenga el dispositivo
"""
@router.post("/users/{user_id}/fingerprint", response_model=user_schemas.User)
async def register_fingerprint(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    try:
        # Conexión con dispositivo ZKTeco
        zk = ZKTeco('IP_DISPOSITIVO', PUERTO)
        template = zk.capture_fingerprint()

        if not template:
            raise HTTPException(
                status_code=400, 
                detail="Error al capturar huella"
            )

        encrypted_template = encrypt_fingerprint(template)
        user.fingerprint_template = encrypted_template
        db.commit()
        db.refresh(user)

        return {
            "message": "Huella registrada exitosamente",
            "user": user
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error con el dispositivo: {str(e)}"
        )
"""
