from pydantic import BaseModel
from typing import Optional

class UserSettings(BaseModel):
    """Pydantic model for user settings"""
    username: str
    email: str
    full_name: str
    default_experience: str
    default_vibe: str

class UpdateSettings(BaseModel):
    """Pydantic model for updating user settings (all fields optional)"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    default_experience: Optional[str] = None
    default_vibe: Optional[str] = None