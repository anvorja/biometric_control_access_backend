from typing import Optional
import base64
import hashlib
import random
from datetime import datetime


class MockZKTeco:
    def __init__(self):
        self._stored_templates = {}
        self._device_status = True
        self._device_id = "ZKTECO_SIMULATOR_001"
        # Simulamos una huella "real" que siempre será la misma en verificación
        self._simulation_template = self._generate_template("fixed_simulation_key")

    def _generate_template(self, key: str) -> str:
        """Genera un template consistente basado en una clave"""
        return base64.b64encode(
            hashlib.sha256(key.encode()).digest()
        ).decode()

    def connect(self) -> bool:
        """Simula la conexión con el dispositivo"""
        return self._device_status

    def disconnect(self) -> bool:
        """Simula la desconexión del dispositivo"""
        return True

    def get_device_info(self) -> dict:
        """Retorna información simulada del dispositivo"""
        return {
            "device_id": self._device_id,
            "firmware_version": "1.0.0",
            "status": "connected" if self._device_status else "disconnected"
        }

    def capture_fingerprint(self, for_verification: bool = False) -> Optional[str]:
        """
       Simula la captura de una huella
       Para verificación, siempre retorna la misma huella
       Para registro, genera una nueva
       """
        if for_verification:
            # En verificación, siempre retorna la misma huella simulada
            return self._simulation_template
        else:
            # Para registro, genera una nueva
            return self._generate_template(f"user_template_{datetime.now().timestamp()}")

    def verify_fingerprint(self, stored_template: str, current_template: str) -> bool:
        """Simula la verificación de una huella"""
        # Para propósitos de simulación, consideramos válida la huella simulada
        return current_template == self._simulation_template

    def store_fingerprint(self, user_id: int, template: str) -> bool:
        """Almacena un template de huella para un usuario"""
        self._stored_templates[user_id] = template
        return True

    def get_stored_template(self, user_id: int) -> Optional[str]:
        """Obtiene el template almacenado de un usuario"""
        return self._stored_templates.get(user_id)


# Funciones de utilidad fuera de la clase
def verify_templates_match(template1: str, template2: str) -> bool:
    """
    Compara dos templates de huella
    En una implementación real, usaría el SDK del dispositivo
    """
    # Aquí iría la lógica real de comparación de huellas
    return template1 == template2  # Simplificado para ejemplo


def validate_template_format(template: str) -> bool:
    """
    Validar que el template tiene el formato correcto
    """
    try:
        # Verificar que el template esté en base64 válido
        base64.b64decode(template)
        return True
    except:
        return False
