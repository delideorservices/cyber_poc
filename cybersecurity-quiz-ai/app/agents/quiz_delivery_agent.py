from typing import Dict, Any
import json
import logging
import re

class QuizDeliveryAgent:
    """Agent for delivering formatted quiz to the frontend"""
    
    def __init__(self):
        """Initialize the quiz delivery agent"""
        self.name = "QuizDeliveryAgent"
        self.description = "Delivers formatted quiz to the frontend"
        self.logger = logging.getLogger(__name__)
    
    def _validate_inputs(self, inputs: Dict[str, Any], required_keys: list) -> None:
        """Validate that required keys are present in inputs"""
        # print("Extracted data from delivery:")
        # for key, value in inputs.items():
        #             print(f"  {key}: {value}")
            # Validate required inputs
        for key in required_keys:
            if key not in inputs:
                raise ValueError(f"Missing required input: {key}")
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process inputs and deliver quiz"""
        try:
            # Add validation for user_id
            if 'user_id' not in inputs or not inputs.get('user_id'):
                self.logger.warning(f"Missing or invalid user_id in inputs: {inputs.get('user_id', 'Not provided')}")
            
            return self._execute(inputs)
        except Exception as e:
            self.logger.error(f"Error in {self.name}: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the quiz delivery process"""
        try:
            # Validate required inputs - quiz_data must come from CrewAI output context
            if 'quiz' not in inputs and 'quiz_data' in inputs:
                inputs['quiz'] = inputs['quiz_data']
            if 'quiz' not in inputs:
                # Try to find quiz inside quiz_data
                if 'quiz_data' in inputs:
                    inputs['quiz'] = inputs['quiz_data']
                # Try to find quiz inside formatted_quiz
                elif 'formatted_quiz' in inputs and 'quiz' in inputs['formatted_quiz']:
                    inputs['quiz'] = inputs['formatted_quiz']['quiz']
                    print(f"Extracted quiz from formatted_quiz: {inputs['quiz'].get('title', 'No title')}")
            self._validate_inputs(inputs, ['quiz'])
            
            # Import dependencies here to avoid circular imports
            from app.services.db_service import db_service
            
            # Get formatted quiz data
            quiz_data = inputs.get('quiz')
            user_id = inputs.get('user_id', 0)
            
            # Log user_id for debugging
            self.logger.info(f"Processing quiz with user_id: {user_id}")
            
            self.logger.info(f"Got quiz data with title: {quiz_data.get('title', 'Untitled Quiz')}")
            
            # Store quiz in database
            quiz_id = self._store_quiz_in_database(db_service, quiz_data, user_id)
            
            if not quiz_id:
                self.logger.error("Failed to store quiz in database")
                return {
                    'status': 'error',
                    'message': 'Failed to store quiz in database'
                }
            
            # Count chapters and questions
            chapters = quiz_data.get('chapters', [])
            chapter_count = len(chapters)
            question_count = sum(len(chapter.get('questions', [])) for chapter in chapters)
            
            self.logger.info(f"Successfully delivered quiz with ID {quiz_id}")
            
            # Return success response
            return {
                'quiz_id': quiz_id,
                'quiz_title': quiz_data.get('title', 'Untitled Quiz'),
                'chapter_count': chapter_count,
                'question_count': question_count,
                'user_id': user_id,
                'status': 'delivered'
            }
        
        except Exception as e:
            self.logger.error(f"Error delivering quiz: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': f'Quiz delivery failed: {str(e)}'
            }
    
    def _store_quiz_in_database(self, db_service, quiz_data: Dict[str, Any], user_id: int) -> int:
        """Store quiz in database"""
        try:
            self.logger.info("Starting database storage process")
            
            # Extract quiz metadata
            title = quiz_data.get('title', 'Untitled Quiz')
            description = quiz_data.get('description', '')
            difficulty_level = quiz_data.get('difficulty_level', 3)
            topic_id = quiz_data.get('topic_id', 1)  # Default topic ID
            
            # Get sector_id and role_id from quiz_data or from the user profile
            sector_id = quiz_data.get('sector_id')
            role_id = quiz_data.get('role_id')
            
            # Log the values for debugging
            self.logger.info(f"Initial values - user_id: {user_id}, sector_id: {sector_id}, role_id: {role_id}")
            
            # If sector_id or role_id is not available in quiz_data, fetch from user profile
            if sector_id is None or role_id is None:
                user_profile = self._get_user_profile(db_service, user_id)
                sector_id = sector_id or user_profile.get('sector_id')
                role_id = role_id or user_profile.get('role_id')
                self.logger.info(f"After profile lookup - sector_id: {sector_id}, role_id: {role_id}")
            
            # Insert quiz record
            self.logger.info(f"Inserting quiz '{title}' into database with user_id: {user_id}, sector_id: {sector_id}, role_id: {role_id}")
            result = db_service.execute_with_return(
                """
                INSERT INTO quizzes 
                (title, description, user_id, topic_id, difficulty_level, sector_id, role_id, status, metadata) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb) 
                RETURNING id
                """,
                (
                    title,
                    description,
                    user_id,
                    topic_id,
                    difficulty_level,
                    sector_id,
                    role_id,
                    'ready',
                    json.dumps(quiz_data)
                )
            )
            
            if not result or len(result) == 0:
                self.logger.error("Database insert failed - no result returned")
                return 0
            
            quiz_id = result[0][0]
            self.logger.info(f"Successfully created quiz with ID: {quiz_id}")
            
            # Store chapters and questions
            self._store_chapters_and_questions(db_service, quiz_id, quiz_data.get('chapters', []))
            
            return quiz_id
        
        except Exception as e:
            self.logger.error(f"Error storing quiz in database: {str(e)}", exc_info=True)
            return 0

    def _get_user_profile(self, db_service, user_id: int) -> Dict[str, Any]:
        """Fetch user profile data including sector_id and role_id"""
        try:
            self.logger.info(f"Fetching profile data for user_id: {user_id}")
            
            result = db_service.execute_with_return(
                """
                SELECT sector_id, role_id FROM users WHERE id = %s
                """,
                (user_id,)
            )
            
            if not result or len(result) == 0:
                self.logger.warning(f"User profile not found for user_id: {user_id}")
                return {'sector_id': None, 'role_id': None}
            
            profile_data = {
                'sector_id': result[0][0],
                'role_id': result[0][1]
            }
            
            self.logger.info(f"Retrieved profile data: {profile_data}")
            return profile_data
        
        except Exception as e:
            self.logger.error(f"Error fetching user profile: {str(e)}", exc_info=True)
            return {'sector_id': None, 'role_id': None}
    
    def _store_chapters_and_questions(self, db_service, quiz_id: int, chapters: list) -> None:
        """Store chapters and questions"""
        try:
            for i, chapter in enumerate(chapters):
                self.logger.info(f"Storing chapter {i+1}: {chapter.get('title', '')}")
                
                # Insert chapter
                chapter_result = db_service.execute_with_return(
                    """
                    INSERT INTO chapters 
                    (quiz_id, title, description, sequence) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING id
                    """,
                    (
                        quiz_id,
                        chapter.get('title', f'Chapter {i+1}'),
                        chapter.get('description', ''),
                        i+1
                    )
                )
                
                if not chapter_result or len(chapter_result) == 0:
                    self.logger.error(f"Failed to insert chapter {i+1}")
                    continue
                
                chapter_id = chapter_result[0][0]
                
                # Store questions
                questions = chapter.get('questions', [])
                for j, question in enumerate(questions):
                    self._store_question(db_service, chapter_id, j+1, question)
                    
            self.logger.info(f"Successfully stored all chapters and questions for quiz {quiz_id}")
        
        except Exception as e:
            self.logger.error(f"Error storing chapters: {str(e)}", exc_info=True)
    
    def _store_question(self, db_service, chapter_id: int, sequence: int, question: Dict[str, Any]) -> None:
        """Store question"""
        try:
            # Extract question data
            q_type = question.get('type', 'mcq')
            content = question.get('content', '')
            options = question.get('options', [])
            correct_answer = question.get('correct_answer', '')
            explanation = question.get('explanation', '')
            points = question.get('points', 3)
            difficulty = question.get('difficulty', 3)
            knowledge_area = question.get('knowledge_area', '')
            
            # Create metadata
            metadata = {
                'knowledge_area': knowledge_area
            }
            
            # Insert question
            db_service.execute(
                """
                INSERT INTO questions 
                (chapter_id, type, content, options, correct_answer, explanation, 
                sequence, points, difficulty, metadata) 
                VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s::jsonb)
                """,
                (
                    chapter_id,
                    q_type,
                    content,
                    json.dumps(options),
                    correct_answer,
                    explanation,
                    sequence,
                    points,
                    difficulty,
                    json.dumps(metadata)
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error storing question: {str(e)}", exc_info=True)
