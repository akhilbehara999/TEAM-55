from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib
import secrets

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    username = Column(String, unique=True, index=True)  # Add username field
    hashed_password = Column(String)
    salt = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Settings fields
    default_experience = Column(String, default="Beginner")  # "Beginner", "Intermediate", "Expert"
    default_vibe = Column(String, default="Startup")  # "Startup", "Corporate", "Non-Profit", "Creative"
    
    def set_password(self, password: str):
        """Hash and set the user's password"""
        self.hashed_password, self.salt = hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash"""
        return verify_password(password, self.hashed_password, self.salt)

def hash_password(password: str) -> tuple[str, str]:
    """Hash a password with a salt"""
    salt = secrets.token_hex(16)
    salted_password = password + salt
    hashed = hashlib.sha256(salted_password.encode()).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify a password against its hash and salt"""
    salted_password = password + salt
    new_hash = hashlib.sha256(salted_password.encode()).hexdigest()
    return new_hash == hashed_password