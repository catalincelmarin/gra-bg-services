from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
