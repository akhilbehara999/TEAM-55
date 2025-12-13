from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models.user import User
from models.history import History
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create tables directly"""
    try:
        # Create database engine
        engine = create_engine(
            "sqlite:///./careerflow.db",
            connect_args={"check_same_thread": False}
        )
        
        # Create all tables
        User.__table__.create(bind=engine, checkfirst=True)
        History.__table__.create(bind=engine, checkfirst=True)
        
        logger.info("Tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = create_tables()
    if success:
        print("Tables created successfully!")
    else:
        print("Failed to create tables!")