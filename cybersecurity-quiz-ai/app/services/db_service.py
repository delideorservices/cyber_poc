import logging
import psycopg2
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging at the module level
logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for the quiz application"""
    
    def __init__(self):
        """Initialize the database service using environment variables"""
        self.db_host = os.getenv("POSTGRES_HOST", "localhost")
        self.db_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.db_name = os.getenv("POSTGRES_DB", "new_cyber_poc")
        self.db_user = os.getenv("POSTGRES_USER", "postgres")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "1234")
        self.logger = logger
    
    def get_connection(self):
        """Get a database connection"""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise
    
    def execute(self, query: str, params=None) -> bool:
        """Execute a query without returning results"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return False
    
    def execute_with_return(self, query: str, params=None) -> Optional[List[Tuple]]:
        """Execute a query and return results"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchall()
                    conn.commit()
            return result
        except Exception as e:
            logger.error(f"Database error in execute_with_return: {str(e)}")
            return None
    
    def fetch_one(self, query: str, params=None) -> Optional[Dict[str, Any]]:
        """Fetch a single row as a dictionary"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    
                    if result:
                        return dict(result)
                    return None
        except Exception as e:
            logger.error(f"Error fetching one row: {str(e)}")
            return None
    
    def fetch_all(self, query: str, params=None) -> List[Dict[str, Any]]:
        """Fetch all rows as dictionaries"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching all rows: {str(e)}")
            return []
    
    def log_agent_action(self, agent_name: str, action: str, input_data: Dict[str, Any], 
                        output_data: Optional[Dict[str, Any]] = None, status: str = "success", 
                        error_message: Optional[str] = None) -> bool:
        """Log agent actions to a log file"""
        try:
            logs_dir = "logs"
            os.makedirs(logs_dir, exist_ok=True)
            
            log_file = os.path.join(logs_dir, "agent_actions.log")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(log_file, "a") as f:
                f.write(f"{timestamp} - {agent_name} - {action} - {status}\n")
                if error_message:
                    f.write(f"  Error: {error_message}\n")
            
            return True
        except Exception as e:
            logger.error(f"Error logging agent action: {str(e)}")
            return False

# Create a singleton instance
db_service = DatabaseService()
