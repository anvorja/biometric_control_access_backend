from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    email: str
    full_name: str


class AccessLogBase(BaseModel):
    access_type: str  # "entry" o "exit"
    device_id: str = "default"  # Valor por defecto si no se especifica


class AccessLogCreate(AccessLogBase):
    pass  # Ya no necesitamos user_id ni status aquí, se manejan internamente


class AccessLog(AccessLogBase):
    id: int
    user_id: int
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True


class AccessLogWithUser(AccessLog):
    user: Optional[UserBase]

    class Config:
        from_attributes = True
