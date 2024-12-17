from sqlalchemy.orm import relationship
from app.models.base_class import Base
from app.models.user import User
from app.models.access_log import AccessLog

# Configurar las relaciones después de que ambos modelos existan
User.access_logs = relationship("AccessLog", back_populates="user")
AccessLog.user = relationship("User", back_populates="access_logs")