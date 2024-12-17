from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.biometric import MockZKTeco
from app.core.security import encrypt_fingerprint, decrypt_fingerprint
from .biometric import MockZKTeco, verify_templates_match, validate_template_format


class FingerprintService:
    def __init__(self):
        self.device = MockZKTeco()

    async def register_fingerprint(self, db: Session, user_id: int) -> Optional[str]:
        """Registra la huella de un usuario"""
        template = self.device.capture_fingerprint(for_verification=False)
        if template and validate_template_format(template):
            return template
        return None

    async def capture_current_fingerprint(self) -> str:
        """Captura la huella actual para verificación"""
        return self.device.capture_fingerprint(for_verification=True)

    async def verify_fingerprint(self, db: Session, template: str) -> Dict:
        """Verifica una huella contra la base de datos"""
        if not validate_template_format(template):
            raise ValueError("Formato de huella inválido")

        users = db.query(User).filter(User.fingerprint_template.isnot(None)).all()
        for user in users:
            # Asegúrate de que user.fingerprint_template se resuelva en una cadena
            stored_template = decrypt_fingerprint(str(user.fingerprint_template))
            if verify_templates_match(template, stored_template):
                return {
                    "is_valid": True,
                    "user_id": user.id,
                    "access_type": "entry"  # Lógica para determinar entry/exit
                }

        return {"is_valid": False}

    async def verify_fingerprint_false(self, db: Session, user_id: int) -> bool:
        """Simula una verificación fallida"""
        return False
