import json
import logging
from datetime import datetime
from database.config import SessionLocal
from models.history import History
import uuid

logger = logging.getLogger(__name__)

class HistoryManager:
    """Manages saving and retrieving history records"""
    
    @staticmethod
    def save_history(user_id: int, agent_name: str, summary_text: str, full_output: dict, action_type: str = "analyze"):
        """
        Save a history record to the database
        
        Args:
            user_id: ID of the user performing the action
            agent_name: Name of the agent used (e.g., "Resume Analyzer")
            summary_text: Brief summary of the result (e.g., "Score: 85")
            full_output: Complete output from the agent
            action_type: Type of action performed (default: "analyze")
            
        Returns:
            History record ID if successful, None otherwise
        """
        db = SessionLocal()
        try:
            # Generate a unique session ID
            session_id = str(uuid.uuid4())
            
            # Convert full_output to JSON string if it's a dict
            full_output_str = full_output if isinstance(full_output, str) else json.dumps(full_output, indent=2)
            
            # Create history record
            history_record = History(
                user_id=user_id,
                session_id=session_id,
                agent_name=agent_name,
                summary_text=summary_text,
                full_output=full_output_str,
                action_type=action_type
            )
            
            # Save to database
            db.add(history_record)
            db.commit()
            db.refresh(history_record)
            
            logger.info(f"Saved history record for user {user_id}, agent {agent_name}")
            return history_record.id
        except Exception as e:
            logger.error(f"Error saving history record: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_user_history(user_id: int, page: int = 1, limit: int = 20):
        """
        Retrieve paginated history records for a user
        
        Args:
            user_id: ID of the user
            page: Page number (1-indexed)
            limit: Number of records per page
            
        Returns:
            Tuple of (total_records, history_records)
        """
        db = SessionLocal()
        try:
            # Calculate offset
            offset = (page - 1) * limit
            
            # Get total count
            total_records = db.query(History).filter(History.user_id == user_id).count()
            
            # Get paginated records
            history_records = db.query(History)\
                .filter(History.user_id == user_id)\
                .order_by(History.timestamp.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            # Convert to dictionaries
            records = [record.to_dict() for record in history_records]
            
            return total_records, records
        except Exception as e:
            logger.error(f"Error retrieving history records: {e}")
            return 0, []
        finally:
            db.close()

# Example usage
if __name__ == "__main__":
    # Example of how to use the HistoryManager
    manager = HistoryManager()
    
    # Save a sample history record
    sample_output = {
        "overall_score": 85,
        "summary": "Good resume with strong technical skills",
        "keywords": ["Python", "JavaScript", "React"]
    }
    
    history_id = manager.save_history(
        user_id=1,
        agent_name="Resume Analyzer",
        summary_text="Score: 85",
        full_output=sample_output
    )
    
    if history_id:
        print(f"Saved history record with ID: {history_id}")
        
        # Retrieve history records
        total, records = manager.get_user_history(user_id=1, page=1, limit=10)
        print(f"Total records: {total}")
        print(f"Records: {records}")