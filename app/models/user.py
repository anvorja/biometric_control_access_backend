from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base_class import Base


class User(Base):
    __tablename__ = 'user'  # Especificamos el nombre de la tabla

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    employee_id = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    fingerprint_template = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con AccessLog
    access_logs = relationship("AccessLog", back_populates="user")
