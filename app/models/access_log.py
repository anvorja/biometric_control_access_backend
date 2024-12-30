from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base_class import Base


class AccessLog(Base):
    __tablename__ = 'access_log'  # Especificamos el nombre de la tabla

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    access_type = Column(String)  # "entry" o "exit"
    status = Column(String)  # "success" o "denied"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    device_id = Column(String)

    # Relación con User
    # user = relationship("User", back_populates="access_logs")
    user = relationship("User", back_populates="access_logs", lazy="joined")
