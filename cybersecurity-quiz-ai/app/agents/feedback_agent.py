from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.db_service import db_service
from app.services.queue_service import queue_service

class FeedbackAgent(BaseAgent):
    """Agent for delivering personalized feedback and recommendations"""
    
    def __init__(self):
        super().__init__(
            name="FeedbackAgent",
            description="Delivers personalized feedback and next quiz recommendations"
        )
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process analytics data and deliver personalized feedback
        
        Args:
            inputs: Dictionary containing analytics data
            
        Returns:
            Dictionary with personalized feedback
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['user_id', 'performance_summary', 'strengths', 'weaknesses', 'improvement_suggestions'])
        
        user_id = inputs['user_id']
        performance = inputs['performance_summary']
        strengths = inputs['strengths']
        weaknesses = inputs['weaknesses']
        suggestions = inputs['improvement_suggestions']
        next_quizzes = inputs.get('next_quiz_recommendations', [])
        
        # Get user info
        user = db_service.fetch_one(
            "SELECT name, email FROM users WHERE id = %s",
            (user_id,)
        )
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Format personalized feedback message
        message = self._format_feedback_message(
            user_name=user['name'],
            performance=performance,
            strengths=strengths, 
            weaknesses=weaknesses,
            suggestions=suggestions,
            next_quizzes=next_quizzes
        )
        
        # Store feedback in database
        feedback_id = db_service.execute_returning(
            """
            INSERT INTO user_feedbacks
            (user_id, feedback_content, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
            RETURNING id
            """,
            (user_id, message)
        )
        
        # Send notification to user (via Redis for frontend to consume)
        queue_service.publish(
            channel='user_notifications',
            message={
                'event': 'new_feedback',
                'user_id': user_id,
                'feedback_id': feedback_id
            }
        )
        
        return {
            'user_id': user_id,
            'feedback_id': feedback_id,
            'message': message,
            'status': 'success'
        }
    
    def _format_feedback_message(self, user_name: str, performance: Dict,
                                strengths: List[Dict], weaknesses: List[Dict],
                                suggestions: List[str], next_quizzes: List[Dict]) -> str:
        """
        Format personalized feedback message
        
        Args:
            user_name: User's name
            performance: Performance summary
            strengths: List of strength areas
            weaknesses: List of weak areas
            suggestions: List of improvement suggestions
            next_quizzes: List of recommended quizzes
            
        Returns:
            Formatted feedback message
        """
        message = f"Hello {user_name},\n\n"
        
        # Add performance summary
        message += "Your Cybersecurity Training Performance:\n"
        message += f"- You've completed {performance['total_quizzes']} quiz(es)\n"
        message += f"- Your average score is {performance['average_score']}%\n"
        
        if performance['trend'] == 'improving':
            message += "- Your scores show an improving trend - great job!\n"
        elif performance['trend'] == 'declining':
            message += "- Your recent scores show a declining trend - time to review\n"
        elif performance['trend'] == 'steady':
            message += "- Your scores have been consistent\n"
        
        # Add strengths
        if strengths:
            message += "\nYour Strengths:\n"
            for i, strength in enumerate(strengths, 1):
                message += f"{i}. {strength['area']} ({strength['score']}%)\n"
        
        # Add areas for improvement
        if weaknesses:
            message += "\nAreas for Improvement:\n"
            for i, weakness in enumerate(weaknesses, 1):
                message += f"{i}. {weakness['area']} ({weakness['score']}%)\n"
        
        # Add improvement suggestions
        if suggestions:
            message += "\nSuggested Improvement Actions:\n"
            for i, suggestion in enumerate(suggestions, 1):
                message += f"{i}. {suggestion}\n"
        
        # Add recommended quizzes
        if next_quizzes:
            message += "\nRecommended Next Quizzes:\n"
            for i, quiz in enumerate(next_quizzes, 1):
                message += f"{i}. {quiz['name']}: {quiz['description']}\n"
        
        # Add closing note
        message += "\nKeep up the good work and continue strengthening your cybersecurity knowledge!"
        
        return message