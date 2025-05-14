import os
import time
import logging
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor, execute_values
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple, Union, Generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db_connector')

# Default connection parameters (override with environment variables)
DEFAULT_CONFIG = {
    'dbname': os.environ.get('DB_DATABASE', 'cybersecurity_quiz'),
    'user': os.environ.get('DB_USERNAME', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', '1234'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'min_connections': int(os.environ.get('DB_MIN_CONNECTIONS', '1')),
    'max_connections': int(os.environ.get('DB_MAX_CONNECTIONS', '10'))
}


class DatabaseConnector:
    """
    A class for managing database connections and operations.
    
    This class provides methods for executing queries, managing transactions,
    and performing CRUD operations on the database.
    """
    
    _instance = None
    _connection_pool = None
    
    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to ensure only one connection pool exists."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the database connector with connection parameters.
        
        Args:
            config: Dictionary containing database connection parameters.
                   If not provided, default values or environment variables are used.
        """
        if DatabaseConnector._connection_pool is not None:
            return
            
        self.config = config or DEFAULT_CONFIG
        self._create_connection_pool()
        logger.info("DatabaseConnector initialized with connection pool")
    
    def _create_connection_pool(self) -> None:
        """Create a connection pool for database connections."""
        try:
            DatabaseConnector._connection_pool = pool.ThreadedConnectionPool(
                minconn=self.config['min_connections'],
                maxconn=self.config['max_connections'],
                dbname=self.config['dbname'],
                user=self.config['user'],
                password=self.config['password'],
                host=self.config['host'],
                port=self.config['port']
            )
            logger.info(f"Connection pool created with {self.config['min_connections']} to "
                        f"{self.config['max_connections']} connections")
        except psycopg2.Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator:
        """
        Get a connection from the pool and return it as a context manager.
        
        Usage:
            with db_connector.get_connection() as conn:
                # use connection
        
        Yields:
            psycopg2.connection: A database connection from the pool
        """
        conn = None
        try:
            conn = DatabaseConnector._connection_pool.getconn()
            yield conn
        except psycopg2.pool.PoolError as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise
        finally:
            if conn:
                DatabaseConnector._connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor) -> Generator:
        """
        Get a cursor from a connection in the pool and return it as a context manager.
        
        Usage:
            with db_connector.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()
        
        Args:
            cursor_factory: The cursor factory to use (default: RealDictCursor)
        
        Yields:
            psycopg2.cursor: A database cursor
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error in database operation: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return the results.
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            List of dictionaries representing query results
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            return []
    
    def execute_batch(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute a batch query with multiple parameter sets.
        
        Args:
            query: SQL query template string
            params_list: List of parameter tuples
        
        Returns:
            Number of rows affected
        """
        with self.get_cursor() as cursor:
            execute_values(cursor, query, params_list)
            return cursor.rowcount
    
    @contextmanager
    def transaction(self) -> Generator:
        """
        Create a transaction context for executing multiple queries atomically.
        
        Usage:
            with db_connector.transaction() as cursor:
                cursor.execute("INSERT INTO users (name) VALUES (%s)", ("John",))
                cursor.execute("INSERT INTO profiles (user_id) VALUES (LASTVAL())")
        
        Yields:
            psycopg2.cursor: A database cursor within a transaction
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                conn.commit()
                logger.info("Transaction committed successfully")
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise
            finally:
                cursor.close()
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a row into a table.
        
        Args:
            table: Table name
            data: Dictionary of column names and values
        
        Returns:
            The ID of the inserted row (if available)
        """
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ', '.join(['%s'] * len(columns))
        column_str = ', '.join(columns)
        
        query = f"INSERT INTO {table} ({column_str}) VALUES ({placeholders}) RETURNING id"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def update(self, table: str, data: Dict[str, Any], condition: str, params: tuple) -> int:
        """
        Update rows in a table.
        
        Args:
            table: Table name
            data: Dictionary of column names and values to update
            condition: WHERE clause
            params: Parameters for the WHERE clause
        
        Returns:
            Number of rows updated
        """
        set_clause = ', '.join([f"{column} = %s" for column in data.keys()])
        values = list(data.values()) + list(params)
        
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount
    
    def delete(self, table: str, condition: str, params: tuple) -> int:
        """
        Delete rows from a table.
        
        Args:
            table: Table name
            condition: WHERE clause
            params: Parameters for the WHERE clause
        
        Returns:
            Number of rows deleted
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive user data including their profile, skills, and certifications.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            Dictionary containing user data
        """
        # Get user profile
        user_query = """
            SELECT u.*, s.name as sector_name, r.name as role_name
            FROM users u
            LEFT JOIN sectors s ON u.sector_id = s.id
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
        """
        
        # Get user skills
        skills_query = """
            SELECT s.id, s.name, s.category, us.proficiency_level
            FROM user_skills us
            JOIN skills s ON us.skill_id = s.id
            WHERE us.user_id = %s
        """
        
        # Get user certifications
        certifications_query = """
            SELECT c.id, c.name, c.issuer, uc.obtained_date, uc.expiry_date
            FROM user_certifications uc
            JOIN certifications c ON uc.certification_id = c.id
            WHERE uc.user_id = %s
        """
        
        user_data = {}
        
        with self.transaction() as cursor:
            # Get user profile
            cursor.execute(user_query, (user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return {}
            
            # Get user skills
            cursor.execute(skills_query, (user_id,))
            user_data['skills'] = cursor.fetchall()
            
            # Get user certifications
            cursor.execute(certifications_query, (user_id,))
            user_data['certifications'] = cursor.fetchall()
        
        return user_data
    
    def save_quiz(self, quiz_data: Dict[str, Any]) -> int:
        """
        Save a quiz and its questions to the database.
        
        Args:
            quiz_data: Dictionary containing quiz data with chapters and questions
        
        Returns:
            ID of the saved quiz
        """
        try:
            with self.transaction() as cursor:
                # Insert quiz
                quiz_query = """
                    INSERT INTO quizzes (
                        title, description, user_id, topic_id, 
                        sector_id, role_id, difficulty_level, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                cursor.execute(
                    quiz_query, 
                    (
                        quiz_data['title'],
                        quiz_data.get('description', ''),
                        quiz_data['user_id'],
                        quiz_data['topic_id'],
                        quiz_data.get('sector_id'),
                        quiz_data.get('role_id'),
                        quiz_data.get('difficulty_level', 3),
                        quiz_data.get('metadata', None)
                    )
                )
                
                quiz_id = cursor.fetchone()['id']
                
                # Insert chapters and questions
                for chapter_idx, chapter in enumerate(quiz_data.get('chapters', [])):
                    # Insert chapter
                    chapter_query = """
                        INSERT INTO chapters (
                            quiz_id, title, description, sequence
                        ) VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """
                    
                    cursor.execute(
                        chapter_query, 
                        (
                            quiz_id,
                            chapter['title'],
                            chapter.get('description', ''),
                            chapter_idx + 1
                        )
                    )
                    
                    chapter_id = cursor.fetchone()['id']
                    
                    # Insert questions
                    for question_idx, question in enumerate(chapter.get('questions', [])):
                        question_query = """
                            INSERT INTO questions (
                                chapter_id, type, content, options,
                                correct_answer, explanation, sequence, points
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        cursor.execute(
                            question_query, 
                            (
                                chapter_id,
                                question.get('type', 'mcq'),
                                question['content'],
                                question.get('options', []),
                                question['correct_answer'],
                                question.get('explanation', ''),
                                question_idx + 1,
                                question.get('points', 1)
                            )
                        )
                
                return quiz_id
                
        except Exception as e:
            logger.error(f"Error saving quiz: {e}")
            raise
    
    def save_quiz_result(self, result_data: Dict[str, Any]) -> int:
        """
        Save a quiz result to the database.
        
        Args:
            result_data: Dictionary containing quiz result data
        
        Returns:
            ID of the saved result
        """
        try:
            with self.transaction() as cursor:
                # Insert quiz result
                result_query = """
                    INSERT INTO user_quiz_results (
                        user_id, quiz_id, score, max_score, 
                        percentage_score, time_spent, feedback
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                cursor.execute(
                    result_query, 
                    (
                        result_data['user_id'],
                        result_data['quiz_id'],
                        result_data['score'],
                        result_data['max_score'],
                        result_data['percentage_score'],
                        result_data.get('time_spent'),
                        result_data.get('feedback')
                    )
                )
                
                result_id = cursor.fetchone()['id']
                
                # Insert user responses
                if 'responses' in result_data:
                    response_query = """
                        INSERT INTO user_responses (
                            user_id, quiz_id, question_id, result_id,
                            user_answer, is_correct, points_earned
                        ) VALUES %s
                    """
                    
                    response_data = [
                        (
                            result_data['user_id'],
                            result_data['quiz_id'],
                            response['question_id'],
                            result_id,
                            response['user_answer'],
                            response['is_correct'],
                            response['points_earned']
                        )
                        for response in result_data['responses']
                    ]
                    
                    execute_values(cursor, response_query, response_data)
                
                return result_id
                
        except Exception as e:
            logger.error(f"Error saving quiz result: {e}")
            raise
    
    def save_learning_plan(self, plan_data: Dict[str, Any]) -> int:
        """
        Save a learning plan and its modules to the database.
        
        Args:
            plan_data: Dictionary containing learning plan data with modules
        
        Returns:
            ID of the saved learning plan
        """
        try:
            with self.transaction() as cursor:
                # Insert learning plan
                plan_query = """
                    INSERT INTO learning_plans (
                        user_id, title, description, focus_areas,
                        target_completion_date, status, difficulty_level,
                        overall_progress, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                cursor.execute(
                    plan_query, 
                    (
                        plan_data['user_id'],
                        plan_data['title'],
                        plan_data.get('description', ''),
                        plan_data.get('focus_areas', []),
                        plan_data.get('target_completion_date'),
                        plan_data.get('status', 'active'),
                        plan_data.get('difficulty_level', 3),
                        plan_data.get('overall_progress', 0),
                        plan_data.get('metadata', {})
                    )
                )
                
                plan_id = cursor.fetchone()['id']
                
                # Insert learning plan modules
                if 'modules' in plan_data:
                    module_query = """
                        INSERT INTO learning_plan_modules (
                            learning_plan_id, title, description, module_type,
                            content_reference_id, sequence, status,
                            estimated_hours, difficulty_level
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """
                    
                    for module_idx, module in enumerate(plan_data['modules']):
                        cursor.execute(
                            module_query, 
                            (
                                plan_id,
                                module['title'],
                                module.get('description', ''),
                                module['module_type'],  # quiz, practice, resource
                                module.get('content_reference_id'),
                                module_idx + 1,
                                module.get('status', 'not_started'),
                                module.get('estimated_hours', 1),
                                module.get('difficulty_level', 3)
                            )
                        )
                
                return plan_id
                
        except Exception as e:
            logger.error(f"Error saving learning plan: {e}")
            raise
    
    def close(self) -> None:
        """Close the connection pool and release all connections."""
        if DatabaseConnector._connection_pool:
            DatabaseConnector._connection_pool.closeall()
            logger.info("Connection pool closed")
            DatabaseConnector._connection_pool = None


# Create a singleton instance for global use
db_connector = DatabaseConnector()


# Helper functions for common database operations
def get_user(user_id: int) -> Dict[str, Any]:
    """Get a user by ID."""
    return db_connector.execute_query(
        "SELECT * FROM users WHERE id = %s", 
        (user_id,)
    )[0] if db_connector.execute_query(
        "SELECT * FROM users WHERE id = %s", 
        (user_id,)
    ) else {}

def get_user_skills(user_id: int) -> List[Dict[str, Any]]:
    """Get skills for a user."""
    return db_connector.execute_query(
        """
        SELECT s.*, us.proficiency_level 
        FROM skills s
        JOIN user_skills us ON s.id = us.skill_id
        WHERE us.user_id = %s
        """, 
        (user_id,)
    )

def get_topic(topic_id: int) -> Dict[str, Any]:
    """Get a topic by ID."""
    return db_connector.execute_query(
        "SELECT * FROM topics WHERE id = %s", 
        (topic_id,)
    )[0] if db_connector.execute_query(
        "SELECT * FROM topics WHERE id = %s", 
        (topic_id,)
    ) else {}

def get_quiz(quiz_id: int) -> Dict[str, Any]:
    """Get a quiz with chapters and questions."""
    quiz = db_connector.execute_query(
        "SELECT * FROM quizzes WHERE id = %s", 
        (quiz_id,)
    )
    
    if not quiz:
        return {}
    
    quiz = quiz[0]
    
    # Get chapters
    chapters = db_connector.execute_query(
        "SELECT * FROM chapters WHERE quiz_id = %s ORDER BY sequence", 
        (quiz_id,)
    )
    
    quiz['chapters'] = []
    
    for chapter in chapters:
        # Get questions for this chapter
        questions = db_connector.execute_query(
            "SELECT * FROM questions WHERE chapter_id = %s ORDER BY sequence", 
            (chapter['id'],)
        )
        
        chapter['questions'] = questions
        quiz['chapters'].append(chapter)
    
    return quiz

def get_quiz_results(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent quiz results for a user."""
    return db_connector.execute_query(
        """
        SELECT qr.*, q.title as quiz_title, q.topic_id, t.name as topic_name
        FROM user_quiz_results qr
        JOIN quizzes q ON qr.quiz_id = q.id
        JOIN topics t ON q.topic_id = t.id
        WHERE qr.user_id = %s
        ORDER BY qr.created_at DESC
        LIMIT %s
        """, 
        (user_id, limit)
    )

def get_learning_plan(user_id: int) -> Dict[str, Any]:
    """Get active learning plan for a user."""
    plans = db_connector.execute_query(
        """
        SELECT * FROM learning_plans 
        WHERE user_id = %s AND status = 'active'
        ORDER BY created_at DESC
        LIMIT 1
        """, 
        (user_id,)
    )
    
    if not plans:
        return {}
    
    plan = plans[0]
    
    # Get modules
    modules = db_connector.execute_query(
        """
        SELECT * FROM learning_plan_modules
        WHERE learning_plan_id = %s
        ORDER BY sequence
        """, 
        (plan['id'],)
    )
    
    plan['modules'] = modules
    
    return plan