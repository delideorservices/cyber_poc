from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
import app.services.db_service as db_service
import logging

class SkillImprovementAgent(BaseAgent):
    """Agent for creating targeted skill improvement activities."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SkillImprovementAgent"
        self.description = "Creates personalized improvement activities based on skill gaps"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user's skill gaps and create improvement opportunities.
        
        Args:
            inputs: Dictionary containing user_id and optionally specific_skills
            
        Returns:
            Dictionary with improvement session details
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['user_id'])
        
        user_id = inputs['user_id']
        specific_skills = inputs.get('specific_skills', None)
        
        # Log the start of execution
        logging.info(f"Generating skill improvement activities for user {user_id}")
        
        # Get user quiz results and identified skill gaps
        user_data = self._get_user_data(user_id)
        
        if not user_data:
            raise ValueError(f"User with ID {user_id} not found")
            
        # Identify skill gaps if not explicitly provided
        skill_gaps = specific_skills if specific_skills else self._get_skill_gaps(user_id)
        
        if not skill_gaps:
            return {
                'user_id': user_id,
                'status': 'no_gaps_found',
                'message': 'No significant skill gaps identified for improvement'
            }
            
        # Create improvement session
        session_id = self._create_improvement_session(user_id, skill_gaps)
        
        # Generate retry activities for each skill gap
        retry_activities = self._generate_retry_activities(user_id, skill_gaps)
        
        # Update session with activities
        self._update_session_with_activities(session_id, retry_activities)
        
        # Create spaced repetition schedule
        repetition_schedule = self._create_repetition_schedule(user_id, skill_gaps)
        
        return {
            'user_id': user_id,
            'session_id': session_id,
            'skill_gaps': skill_gaps,
            'retry_activities': retry_activities,
            'repetition_schedule': repetition_schedule,
            'status': 'success',
            'next_agent': 'QuizGeneratorAgent'
        }
        
    def _get_user_data(self, user_id):
        """Retrieve user profile and performance data"""
        user = db_service.fetch_one(
            "SELECT u.*, r.role_name as role_name, s.name as sector_name "
            "FROM users u "
            "LEFT JOIN sectors s ON u.sector_id = s.id "
            "LEFT JOIN roles r ON u.role_id = r.id "
            "WHERE u.id = %s",
            (user_id,)
        )
        return user
        
    def _get_skill_gaps(self, user_id):
        """Retrieve identified skill gaps for the user"""
        # Get the most recent quiz result with skill gaps
        result = db_service.fetch_one(
            "SELECT skill_gaps FROM user_quiz_results "
            "WHERE user_id = %s AND skill_gaps IS NOT NULL "
            "ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        
        return result['skill_gaps'] if result else None
        
    def _create_improvement_session(self, user_id, skill_gaps):
        """Create a new skill improvement session"""
        result = db_service.execute_returning(
            "INSERT INTO skill_improvement_sessions "
            "(user_id, skill_gaps, status) "
            "VALUES (%s, %s, %s) "
            "RETURNING id",
            (user_id, skill_gaps, 'created')
        )
        return result['id']
        
    def _generate_retry_activities(self, user_id, skill_gaps):
        """Generate retry activities for each skill gap"""
        activities = []
        
        for skill in skill_gaps:
            skill_id = skill['id']
            proficiency = skill.get('current_proficiency', 0)
            
            # Get questions related to this skill that the user answered incorrectly
            questions = db_service.fetch_all(
                "SELECT q.* FROM questions q "
                "JOIN user_responses ur ON q.id = ur.question_id "
                "JOIN chapters c ON q.chapter_id = c.id "
                "JOIN quizzes qz ON c.quiz_id = qz.id "
                "WHERE ur.user_id = %s AND ur.is_correct = false "
                "AND qz.topic_id IN ("
                "  SELECT topic_id FROM topic_skills WHERE skill_id = %s"
                ")",
                (user_id, skill_id)
            )
            
            # Create activity object
            activity = {
                'skill_id': skill_id,
                'skill_name': skill['name'],
                'current_proficiency': proficiency,
                'target_proficiency': proficiency + 1,
                'questions': questions,
                'difficulty_level': min(proficiency + 1, 5)
            }
            
            activities.append(activity)
            
        return activities
        
    def _update_session_with_activities(self, session_id, activities):
        """Update session with generated activities"""
        db_service.execute(
            "UPDATE skill_improvement_sessions "
            "SET activities = %s, updated_at = NOW() "
            "WHERE id = %s",
            (activities, session_id)
        )
        
    def _create_repetition_schedule(self, user_id, skill_gaps):
        """Create spaced repetition schedule for the identified skill gaps"""
        # Initialize spaced repetition intervals (in days)
        intervals = [1, 3, 7, 14, 30]
        
        schedule = []
        
        for skill in skill_gaps:
            skill_id = skill['id']
            
            # Create schedule entries for each interval
            for i, interval in enumerate(intervals):
                scheduled_date = db_service.execute_returning(
                    "SELECT NOW() + INTERVAL '%s DAY' as date", 
                    (interval,)
                )['date']
                
                # Create schedule record
                schedule_id = db_service.execute_returning(
                    "INSERT INTO spaced_repetition_schedules "
                    "(user_id, skill_id, repetition_number, scheduled_date, status) "
                    "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (user_id, skill_id, i+1, scheduled_date, 'scheduled')
                )['id']
                
                schedule.append({
                    'id': schedule_id,
                    'skill_id': skill_id,
                    'skill_name': skill['name'],
                    'repetition_number': i+1,
                    'scheduled_date': scheduled_date,
                    'status': 'scheduled'
                })
                
        return schedule