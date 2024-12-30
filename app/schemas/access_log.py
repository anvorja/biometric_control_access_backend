# schemas/access_log.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict



class UserBase(BaseModel):
    email: str
    full_name: str
    #employee_id: Optional[int] = None
    employee_id: str

    model_config = ConfigDict(from_attributes=True)


class AccessLogBase(BaseModel):
    access_type: str  # "entry" o "exit"
    device_id: str = "default"  # Valor por defecto si no se especifica

    model_config = ConfigDict(from_attributes=True)


class AccessLogCreate(AccessLogBase):
    pass  # Ya no necesitamos user_id ni status aquí, se manejan internamente


class AccessLog(AccessLogBase):
    id: int
    user_id: int
    status: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AccessLogWithUser(AccessLog):
    user: Optional[UserBase]

    model_config = ConfigDict(from_attributes=True)
