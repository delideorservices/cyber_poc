import psycopg2
import psycopg2.extras
import json
from contextlib import contextmanager
from app.config import DATABASE_URL

class DatabaseService:
    @contextmanager
    def get_connection(self):
        """Get a PostgreSQL connection from the pool"""
        conn = psycopg2.connect(DATABASE_URL)
        try:
            yield conn
        finally:
            conn.close()
            
    def fetch_one(self, query, params=None):
        """Execute query and return one result"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, params or ())
                result = cur.fetchone()
                return dict(result) if result else None
                
    def fetch_all(self, query, params=None):
        """Execute query and return all results"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, params or ())
                results = cur.fetchall()
                return [dict(row) for row in results]
                
    def execute(self, query, params=None):
        """Execute query with no return"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                conn.commit()
                
    def execute_returning(self, query, params=None):
        """Execute query and return a single value or ID"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                result = cur.fetchone()
                conn.commit()
                return result[0] if result else None
                
    # Agent log helper
    def log_agent_action(self, agent_name, action, input_data=None, output_data=None, 
                         status="success", error_message=None):
        """Log agent actions to the database"""
        query = """
        INSERT INTO agent_logs 
        (agent_name, action, input, output, status, error_message, executed_at, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), NOW())
        """
        # Convert dict to JSON string for storage
        input_json = json.dumps(input_data) if input_data else None
        output_json = json.dumps(output_data) if output_data else None
        
        self.execute(query, (agent_name, action, input_json, output_json, status, error_message))

# Create a singleton instance
db_service = DatabaseService()