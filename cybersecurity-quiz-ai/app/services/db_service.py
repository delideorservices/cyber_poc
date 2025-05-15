import logging
import psycopg2
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
import psycopg2.extras
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
                try:
                    # Try to use DictCursor if available
                    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        cursor.execute(query, params)
                        result = cursor.fetchone()
                        
                        if result:
                            return dict(result)
                        return None
                except AttributeError:
                    # Fall back to regular cursor if extras is not available
                    with conn.cursor() as cursor:
                        cursor.execute(query, params)
                        result = cursor.fetchone()
                        
                        if result:
                            # If we don't have DictCursor, construct a dict manually
                            # by getting column names from cursor.description
                            column_names = [desc[0] for desc in cursor.description]
                            return dict(zip(column_names, result))
                        return None
        except Exception as e:
            logger.error(f"Error fetching one row: {str(e)}")
            return None

    def fetch_all(self, query: str, params=None) -> List[Dict[str, Any]]:
        """Fetch all rows as dictionaries"""
        try:
            with self.get_connection() as conn:
                try:
                    # Try to use DictCursor if available
                    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        cursor.execute(query, params)
                        results = cursor.fetchall()
                        
                        return [dict(row) for row in results]
                except AttributeError:
                    # Fall back to regular cursor if extras is not available
                    with conn.cursor() as cursor:
                        cursor.execute(query, params)
                        results = cursor.fetchall()
                        
                        # If we don't have DictCursor, construct dicts manually
                        column_names = [desc[0] for desc in cursor.description]
                        return [dict(zip(column_names, row)) for row in results]
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
    def get_skill_performance(self, user_id, topic_id=None, time_period=None):
        """
        Get detailed skill performance metrics for a user
        Optionally filtered by topic or time period
        """
        query_params = [user_id]
        
        query = """
            SELECT 
                s.id as skill_id,
                s.name as skill_name,
                COUNT(DISTINCT ur.question_id) as total_questions,
                SUM(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) as correct_answers,
                SUM(ur.points_earned) as points_earned,
                AVG(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) * 100 as score_percentage
            FROM user_responses ur
            JOIN questions q ON ur.question_id = q.id
            JOIN chapters c ON q.chapter_id = c.id
            JOIN quizzes qz ON c.quiz_id = qz.id
            JOIN skills s ON q.skill_id = s.id
            WHERE ur.user_id = %s
        """
        
        if topic_id:
            query += " AND qz.topic_id = %s"
            query_params.append(topic_id)
        
        if time_period:
            query += " AND ur.created_at >= NOW() - INTERVAL %s"
            query_params.append(time_period)
        
        query += " GROUP BY s.id, s.name"
        
        return self.fetch_all(query, tuple(query_params))

    def get_topic_performance(self, user_id, sector_id=None):
        """
        Get performance metrics aggregated by topic
        Optionally filtered by sector
        """
        query_params = [user_id]
        
        query = """
            SELECT 
                t.id as topic_id,
                t.name as topic_name,
                COUNT(DISTINCT qz.id) as quiz_count,
                AVG(uqr.percentage_score) as avg_score,
                MAX(uqr.created_at) as last_attempt
            FROM user_quiz_results uqr
            JOIN quizzes qz ON uqr.quiz_id = qz.id
            JOIN topics t ON qz.topic_id = t.id
            WHERE uqr.user_id = %s
        """
        
        if sector_id:
            query += " AND t.sector_id = %s"
            query_params.append(sector_id)
        
        query += " GROUP BY t.id, t.name"
        
        return self.fetch_all(query, tuple(query_params))

    def get_learning_resources(self, skill_ids):
        """
        Get learning resources for specific skills
        """
        if not skill_ids:
            return []
            
        placeholders = ', '.join(['%s'] * len(skill_ids))
        query = f"""
            SELECT * FROM learning_resources
            WHERE skill_id IN ({placeholders})
            ORDER BY skill_id, effectiveness_rating DESC
        """
        
        return self.fetch_all(query, tuple(skill_ids))
    def execute_returning(self, query: str, params=None) -> Any:
        """Execute a query and return a single value from the RETURNING clause"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    conn.commit()
                    
                    # Debug the result
                    print(f"execute_returning result: {result}, type: {type(result)}")
                    
                    # If result is a tuple, return the first element
                    if result and isinstance(result, tuple) and len(result) > 0:
                        print(f"Returning first element: {result[0]}, type: {type(result[0])}")
                        return result[0]
                    
                    # If result is a list, return the first element
                    if result and isinstance(result, list) and len(result) > 0:
                        print(f"Returning first element of list: {result[0]}, type: {type(result[0])}")
                        return result[0]
                    
                    return result
        except Exception as e:
            logger.error(f"Error in execute_returning: {str(e)}")
            print(f"Error in execute_returning: {str(e)}")
            # Print the full traceback for debugging
            import traceback
            traceback.print_exc()
            raise


    def get_peer_performance(self, user_id, similar_criteria):
        """
        Get performance metrics for peers with similar criteria
        similar_criteria should be a dict with keys like sector_id, role_id, etc.
        """
        where_clauses = []
        query_params = []
        
        for key, value in similar_criteria.items():
            if isinstance(value, tuple) and len(value) == 2:
                # Range values (e.g., years_experience between min and max)
                where_clauses.append(f"{key} BETWEEN %s AND %s")
                query_params.extend(value)
            else:
                # Exact match
                where_clauses.append(f"{key} = %s")
                query_params.append(value)
        
        # Exclude the current user
        where_clauses.append("id != %s")
        query_params.append(user_id)
        
        # Create the WHERE clause
        where_clause = " AND ".join(where_clauses)
        
        # Get similar users
        similar_users_query = f"""
            SELECT id FROM users 
            WHERE {where_clause}
            LIMIT 100
        """
        
        similar_users = self.fetch_all(similar_users_query, tuple(query_params))
        similar_user_ids = [u['id'] for u in similar_users]
        
        if not similar_user_ids:
            return {
                'status': 'no_peers',
                'users': []
            }
        
        # Get aggregate performance for these users
        performance_query = """
            SELECT 
                s.id as skill_id,
                s.name as skill_name,
                AVG(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) * 100 as avg_score,
                COUNT(DISTINCT ur.user_id) as user_count
            FROM user_responses ur
            JOIN questions q ON ur.question_id = q.id
            JOIN skills s ON q.skill_id = s.id
            WHERE ur.user_id IN %s
            GROUP BY s.id, s.name
        """
        
        performance = self.fetch_all(performance_query, (tuple(similar_user_ids),))
        
        return {
            'status': 'success',
            'user_count': len(similar_user_ids),
            'performance': performance
        }
# Create a singleton instance
db_service = DatabaseService()
