# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.api import deps
# from app.core.security import decrypt_fingerprint, encrypt_fingerprint
# from app.services.fingerprint_service import FingerprintService
# from app.models.user import User
# from app.models.access_log import AccessLog
# from datetime import datetime
#
# router = APIRouter()
# fingerprint_service = FingerprintService()
#
#
# @router.post("/register/{user_id}")
# async def register_fingerprint(
#         user_id: int,
#         db: Session = Depends(deps.get_db),
#         current_user: User = Depends(deps.get_current_admin)
# ):
#     """Registrar huella de un usuario (solo admin)"""
#     template = await fingerprint_service.register_fingerprint(db, user_id)
#     if not template:
#         raise HTTPException(status_code=400, detail="Error al registrar huella")
#     return {"message": "Huella registrada exitosamente"}
#
#
# @router.post("/verify/{user_id}")
# async def verify_fingerprint(
#         user_id: int,
#         db: Session = Depends(deps.get_db),
# ):
#     """Verificar huella de un usuario"""
#     is_valid = await fingerprint_service.verify_fingerprint(db, user_id)
#     return {"is_valid": is_valid}
#
#
# @router.post("/verify-false/{user_id}")
# async def verify_fingerprint_false(
#     user_id: int,
#     db: Session = Depends(deps.get_db),
# ):
#     """Verificar huella de un usuario contra una huella incorrecta (siempre fallará)"""
#     is_valid = await fingerprint_service.verify_fingerprint_false(db, user_id)
#     return {"is_valid": is_valid, "message": "Verificación fallida - Huella no coincide"}
#
#
# @router.post("/users/{user_id}/fingerprint")
# async def register_fingerprint(
#         user_id: int,
#         template: str,
#         db: Session = Depends(deps.get_db),
#         current_user: User = Depends(deps.get_current_admin)
# ):
#     """Registrar huella para un usuario (solo admin)"""
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuario no encontrado")
#
#     encrypted_template = encrypt_fingerprint(template)
#     user.fingerprint_template = encrypted_template
#     db.commit()
#
#     return {"message": "Huella registrada exitosamente"}
#
#
# @router.post("/verify")
# async def verify_fingerprint(
#         template: str,
#         db: Session = Depends(deps.get_db)
# ):
#     """Verificar huella y registrar acceso"""
#     # Buscar usuario por huella
#     users = db.query(User).filter(User.fingerprint_template.isnot(None)).all()
#
#     for user in users:
#         stored_template = decrypt_fingerprint(user.fingerprint_template)
#         if verify_templates_match(template, stored_template):
#             # Registrar acceso
#             access_log = AccessLog(
#                 user_id=user.id,
#                 access_type="entry",  # o determinar si es entry/exit
#                 status="success"
#             )
#             db.add(access_log)
#             db.commit()
#             return {"user_id": user.id, "status": "success"}
#
#     raise HTTPException(status_code=401, detail="Huella no reconocida")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.core.security import decrypt_fingerprint, encrypt_fingerprint
from app.services.fingerprint_service import FingerprintService
from app.models.user import User
from app.models.access_log import AccessLog
from datetime import datetime

router = APIRouter()
fingerprint_service = FingerprintService()


@router.post("/register/{user_id}")
async def register_fingerprint(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin)
):
    """Registrar huella de un usuario (solo admin)"""
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

    return {"message": "Huella registrada exitosamente"}


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
