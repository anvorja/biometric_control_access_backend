from app.models.base_class import Base
from app.models.user import User
from app.models.access_log import AccessLog

# Exportar los modelos para que estén disponibles al importar desde app.models
__all__ = ["Base", "User", "AccessLog"]
