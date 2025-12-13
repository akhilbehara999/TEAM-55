from database.config import engine, Base
from models.user import User
from models.history import History
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database and create tables"""
    try:
        # Import all models to ensure they are registered with Base
        from models.user import User
        from models.history import History
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

def upgrade_db():
    """Upgrade the database schema"""
    try:
        # Import all models to ensure they are registered with Base
        from models.user import User
        from models.history import History
        
        # Create new tables or add new columns
        User.__table__.create(bind=engine, checkfirst=True)
        History.__table__.create(bind=engine, checkfirst=True)
        
        logger.info("Database upgraded successfully!")
        return True
    except Exception as e:
        logger.error(f"Error upgrading database: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    if success:
        print("Database initialization completed successfully!")
    else:
        print("Database initialization failed!")