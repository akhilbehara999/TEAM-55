import sqlite3
import os
from database.config import engine
from models.user import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Add new columns to existing users table"""
    try:
        # Connect to the database
        conn = sqlite3.connect('careerflow.db')
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add username column if it doesn't exist
        if 'username' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN username VARCHAR")
            logger.info("Added username column to users table")
        
        # Add default_experience column if it doesn't exist
        if 'default_experience' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN default_experience VARCHAR DEFAULT 'Beginner'")
            logger.info("Added default_experience column to users table")
        
        # Add default_vibe column if it doesn't exist
        if 'default_vibe' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN default_vibe VARCHAR DEFAULT 'Startup'")
            logger.info("Added default_vibe column to users table")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        logger.info("Database migration completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error migrating database: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("Database migration completed successfully!")
    else:
        print("Database migration failed!")