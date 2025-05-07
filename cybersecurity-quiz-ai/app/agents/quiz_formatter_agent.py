from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.db_service import db_service

class QuizFormatterAgent(BaseAgent):
    """Agent for formatting quiz data for frontend display"""
    
    def __init__(self):
        super().__init__(
            name="QuizFormatterAgent",
            description="Formats quiz content for frontend display"
        )
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format quiz data for frontend display
        
        Args:
            inputs: Dictionary containing generated quiz data
            
        Returns:
            Dictionary with formatted quiz data
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['quiz_id'])
        
        quiz_id = inputs['quiz_id']
        
        # Get quiz data
        quiz = db_service.fetch_one(
            """
            SELECT q.*, t.name as topic_name, u.name as user_name
            FROM quizzes q
            JOIN topics t ON q.topic_id = t.id
            JOIN users u ON q.user_id = u.id
            WHERE q.id = %s
            """,
            (quiz_id,)
        )
        
        if not quiz:
            raise ValueError(f"Quiz with ID {quiz_id} not found")
        
        # Get chapters
        chapters = db_service.fetch_all(
            """
            SELECT * FROM chapters
            WHERE quiz_id = %s
            ORDER BY sequence
            """,
            (quiz_id,)
        )
        
        formatted_chapters = []
        
        for chapter in chapters:
            chapter_id = chapter['id']
            
            # Get questions
            questions = db_service.fetch_all(
                """
                SELECT * FROM questions
                WHERE chapter_id = %s
                ORDER BY sequence
                """,
                (chapter_id,)
            )
            
            formatted_questions = []
            
            for question in questions:
                # Format question data for frontend
                formatted_question = {
                    'id': question['id'],
                    'type': question['type'],
                    'content': question['content'],
                    'options': question['options'],
                    'sequence': question['sequence'],
                    'points': question['points'],
                    # Don't include correct answer in frontend data
                }
                
                formatted_questions.append(formatted_question)
            
            # Format chapter data
            formatted_chapter = {
                'id': chapter['id'],
                'title': chapter['title'],
                'description': chapter['description'],
                'sequence': chapter['sequence'],
                'questions': formatted_questions
            }
            
            formatted_chapters.append(formatted_chapter)
        
        # Prepare formatted quiz data
        formatted_quiz = {
            'id': quiz['id'],
            'title': quiz['title'],
            'description': quiz['description'],
            'topic_name': quiz['topic_name'],
            'difficulty_level': quiz['difficulty_level'],
            'chapters': formatted_chapters,
            'user_id': quiz['user_id'],
            'user_name': quiz['user_name'],
            'created_at': str(quiz['created_at'])
        }
        
        return {
            'quiz': formatted_quiz,
            'status': 'success',
            'next_agent': 'quiz_delivery'
        }