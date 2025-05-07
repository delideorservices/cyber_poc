from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.services.db_service import db_service
from app.services.queue_service import queue_service

class QuizDeliveryAgent(BaseAgent):
    """Agent for delivering formatted quiz to the frontend"""
    
    def __init__(self):
        super().__init__(
            name="QuizDeliveryAgent",
            description="Delivers formatted quiz to the frontend"
        )
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deliver formatted quiz to the frontend
        
        Args:
            inputs: Dictionary containing formatted quiz data
            
        Returns:
            Dictionary with delivery status
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['quiz'])
        
        quiz = inputs['quiz']
        
        # Publish quiz to Redis channel for frontend to consume
        queue_service.publish(
            channel='quiz_ready',
            message={
                'event': 'quiz_ready',
                'quiz_id': quiz['id'],
                'user_id': quiz['user_id']
            }
        )
        
        # Update quiz metadata to indicate it's ready
        db_service.execute(
            """
            UPDATE quizzes
            SET metadata = jsonb_set(
                COALESCE(metadata::jsonb, '{}'::jsonb),
                '{status}',
                '"ready"'
            )
            WHERE id = %s
            """,
            (quiz['id'],)
        )

        
        return {
            'quiz_id': quiz['id'],
            'user_id': quiz['user_id'],
            'status': 'delivered',
            'message': 'Quiz delivered successfully'
        }