from database.config import SessionLocal
from models.user import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_user():
    """Create a test user for development"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.id == 1).first()
        if existing_user:
            logger.info("Test user already exists")
            return existing_user
            
        # Create test user
        user = User(
            id=1,
            email="test@example.com",
            full_name="Test User",
            username="testuser"
        )
        user.set_password("password123")
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info("Test user created successfully")
        return user
    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    user = create_test_user()
    if user:
        print(f"Test user created/exists: {user.email}")
    else:
        print("Failed to create test user")