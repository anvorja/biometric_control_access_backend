from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional
import re
from datetime import datetime
from app.core.validation_utils import InputValidator


# Esquema base para User
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    employee_id: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

    @field_validator('email')
    def validate_email(cls, value):
        # Validar formato de email
        if not InputValidator.validate_email(value):
            raise ValueError('Formato de email inválido')
        # Convertir a minúsculas
        return InputValidator.format_email(value)

    @field_validator('full_name')
    def validate_full_name(cls, value):
        # Validar nombre
        is_valid, error_message = InputValidator.validate_name(value)
        if not is_valid:
            raise ValueError(error_message)

        # Sanitizar y formatear
        sanitized = InputValidator.sanitize_input(value)
        return InputValidator.format_name(sanitized)

    @field_validator('employee_id')
    def validate_employee_id(cls, value):
        # Sanitizar entrada
        sanitized = InputValidator.sanitize_input(value)
        if not sanitized:
            raise ValueError('El ID de empleado no puede estar vacío')
        if len(sanitized) < 3:
            raise ValueError('El ID de empleado debe tener al menos 3 caracteres')
        return sanitized


# Esquema para crear usuario
class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password(cls, value):
        # Sanitizar entrada
        sanitized = InputValidator.sanitize_input(value)
        if not sanitized:
            raise ValueError('La contraseña no puede estar vacía')
        if len(sanitized) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        # Validar complejidad de contraseña
        if not re.search(r'[A-Z]', sanitized):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', sanitized):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'\d', sanitized):
            raise ValueError('La contraseña debe contener al menos un número')
        return sanitized


# Esquema para actualizar usuario
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    fingerprint_template: Optional[str] = None
    is_active: Optional[bool] = None
    employee_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    # Reutilizamos los validadores de UserBase
    _validate_email = UserBase.validate_email
    _validate_full_name = UserBase.validate_full_name
    _validate_employee_id = UserBase.validate_employee_id
    _validate_password = UserCreate.validate_password


# Esquema para respuesta de usuario
class User(UserBase):
    id: int
    is_superuser: bool
    fingerprint_template: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
