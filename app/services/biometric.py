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
        # Agregar manejo de errores del dispositivo
        # try:
        #     if not self._device_status:
        #         raise Exception("Device not connected")
        #
        #     if for_verification:
        #         # En verificación, siempre retorna la misma huella simulada
        #         return self._simulation_template
        #     return self._generate_template(f"user_template_{datetime.now().timestamp()}")
        #
        # except Exception as e:
        #     # Log del error
        #     return None
        ## sugerencia de claude ba653
        class DeviceNotConnectedError(Exception):
            """Error específico para cuando el dispositivo no está conectado"""
            pass

        class CaptureFingerprintError(Exception):
            """Error específico para fallos en la captura de huella"""
            pass

        class MockZKTeco:
            def capture_fingerprint(self, for_verification: bool = False) -> Optional[str]:
                """
                Simula la captura de una huella digital
                Raises:
                    DeviceNotConnectedError: Si el dispositivo no está conectado
                    CaptureFingerprintError: Si hay un error durante la captura
                """
                try:
                    if not self._device_status:
                        raise DeviceNotConnectedError("Device is not connected")

                    if for_verification:
                        if not self._simulation_template:
                            raise CaptureFingerprintError("No simulation template available")
                        return self._simulation_template

                    template = self._generate_template(
                        f"user_template_{datetime.now().timestamp()}"
                    )
                    if not template:
                        raise CaptureFingerprintError("Failed to generate template")

                    return template

                except DeviceNotConnectedError:
                    # Podríamos loggear el error aquí
                    raise
                except CaptureFingerprintError:
                    # Podríamos loggear el error aquí
                    raise
                except Exception as e:
                    # Log error inesperado
                    raise CaptureFingerprintError(f"Unexpected error during capture: {str(e)}")

    # def verify_fingerprint(self, stored_template: str, current_template: str) -> bool:
    #     """Simula la verificación de una huella"""
    #     # Para propósitos de simulación, consideramos válida la huella simulada
    #     return current_template == self._simulation_template
    ## sugerencia de claude ba653
    async def verify_fingerprint(self, db: Session, template: str) -> Dict:
        try:
            if not validate_template_format(template):
                raise ValueError("Invalid fingerprint format")

            # Agregar cache para usuarios con huella
            users = db.query(User).filter(
                User.fingerprint_template.isnot(None),
                User.is_active == True  # Solo usuarios activos
            ).all()

            # Agregar métricas de verificación
            match_found = False
            for user in users:
                stored_template = decrypt_fingerprint(str(user.fingerprint_template))
                match_found = verify_templates_match(template, stored_template)

                if match_found:
                    return {
                        "is_valid": True,
                        "user_id": user.id,
                        "access_type": self._determine_access_type(user.id),
                        "timestamp": datetime.now()
                    }

            return {
                "is_valid": False,
                "error": "No matching fingerprint found"
            }
        except Exception as e:
            return {
                "is_valid": False,
                "error": str(e)
            }

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
