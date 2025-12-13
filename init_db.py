from database.config import engine, Base
from models.user import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database and create tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    if success:
        print("Database initialization completed successfully!")
    else:
        print("Database initialization failed!")