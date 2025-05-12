from typing import Dict, List, Any
import logging
import app.services.db_service as db_service

class ProgressiveDifficultyEngine:
    """
    Engine for dynamically adjusting question difficulty based on user performance.
    
    The engine uses a sliding window approach to evaluate recent performance and 
    adjusts difficulty upward or downward accordingly to maintain an optimal 
    learning challenge level.
    """
    
    def __init__(self, 
                 performance_window: int = 5, 
                 success_threshold: float = 0.8, 
                 struggle_threshold: float = 0.4):
        """
        Initialize the Progressive Difficulty Engine.
        
        Args:
            performance_window: Number of recent questions to consider for difficulty adjustment
            success_threshold: Success rate above which difficulty is increased
            struggle_threshold: Success rate below which difficulty is decreased
        """
        self.performance_window = performance_window
        self.success_threshold = success_threshold
        self.struggle_threshold = struggle_threshold
        self.logger = logging.getLogger(__name__)
        
    def calculate_next_difficulty(self, user_id: int, skill_id: int, current_difficulty: int = None) -> int:
        """
        Calculate the next appropriate difficulty level based on recent performance.
        
        Args:
            user_id: The ID of the user
            skill_id: The ID of the skill to evaluate
            current_difficulty: Current difficulty level (1-5), if None will fetch from DB
            
        Returns:
            Recommended difficulty level (1-5)
        """
        # Get current difficulty if not provided
        if current_difficulty is None:
            # Try to get from skill improvement session
            session = db_service.fetch_one(
                "SELECT activities FROM skill_improvement_sessions "
                "WHERE user_id = %s AND status = 'active' "
                "ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            
            if session and session['activities']:
                activities = session['activities']
                for activity in activities:
                    if activity.get('skill_id') == skill_id:
                        current_difficulty = activity.get('difficulty_level', 3)
                        break
            
            # Default to mid-level if not found
            if current_difficulty is None:
                current_difficulty = 3
                
        # Get recent performance for this skill
        recent_responses = self._get_recent_responses(user_id, skill_id)
        
        if not recent_responses:
            # No history, maintain current difficulty
            self.logger.info(f"No performance history for user {user_id}, skill {skill_id}. Maintaining difficulty {current_difficulty}")
            return current_difficulty
            
        # Calculate success rate
        success_rate = self._calculate_success_rate(recent_responses)
        
        # Determine whether to adjust difficulty
        if success_rate >= self.success_threshold and current_difficulty < 5:
            # User is doing well, increase difficulty
            new_difficulty = min(current_difficulty + 1, 5)
            self.logger.info(f"User {user_id} performing well ({success_rate:.2f}) on skill {skill_id}. "
                            f"Increasing difficulty from {current_difficulty} to {new_difficulty}")
        elif success_rate <= self.struggle_threshold and current_difficulty > 1:
            # User is struggling, decrease difficulty
            new_difficulty = max(current_difficulty - 1, 1)
            self.logger.info(f"User {user_id} struggling ({success_rate:.2f}) on skill {skill_id}. "
                            f"Decreasing difficulty from {current_difficulty} to {new_difficulty}")
        else:
            # User is in optimal challenge zone, maintain difficulty
            new_difficulty = current_difficulty
            self.logger.info(f"User {user_id} in optimal zone ({success_rate:.2f}) for skill {skill_id}. "
                            f"Maintaining difficulty at {current_difficulty}")
            
        return new_difficulty
        
    def generate_questions(self, topic_id: int, skill_id: int, difficulty: int, count: int = 5) -> List[Dict]:
        """
        Generate questions at the specified difficulty level for a skill within a topic.
        
        Args:
            topic_id: The topic ID
            skill_id: The skill ID to focus on
            difficulty: Target difficulty level (1-5)
            count: Number of questions to generate
            
        Returns:
            List of question objects at the appropriate difficulty level
        """
        # Find questions related to the skill in this topic
        questions = db_service.fetch_all(
            "SELECT q.* FROM questions q "
            "JOIN chapters c ON q.chapter_id = c.id "
            "JOIN quizzes qz ON c.quiz_id = qz.id "
            "JOIN topic_skills ts ON qz.topic_id = ts.topic_id "
            "WHERE ts.skill_id = %s AND qz.topic_id = %s "
            "ORDER BY RANDOM() LIMIT %s",
            (skill_id, topic_id, count * 3)  # Fetch more than needed to allow filtering
        )
        
        if not questions:
            self.logger.warning(f"No questions found for topic {topic_id}, skill {skill_id}")
            return []
            
        # Filter and adjust questions to match target difficulty
        selected_questions = self._adjust_questions_difficulty(questions, difficulty, count)
        
        return selected_questions
        
    def _get_recent_responses(self, user_id: int, skill_id: int) -> List[Dict]:
        """Get the user's most recent responses for questions related to the skill"""
        responses = db_service.fetch_all(
            "SELECT ur.* FROM user_responses ur "
            "JOIN questions q ON ur.question_id = q.id "
            "JOIN chapters c ON q.chapter_id = c.id "
            "JOIN quizzes qz ON c.quiz_id = qz.id "
            "JOIN topic_skills ts ON qz.topic_id = ts.topic_id "
            "WHERE ur.user_id = %s AND ts.skill_id = %s "
            "ORDER BY ur.answered_at DESC LIMIT %s",
            (user_id, skill_id, self.performance_window)
        )
        return responses
        
    def _calculate_success_rate(self, responses: List[Dict]) -> float:
        """Calculate success rate from a list of responses"""
        if not responses:
            return 0.0
            
        correct_count = sum(1 for r in responses if r['is_correct'])
        return correct_count / len(responses)
        
    def _adjust_questions_difficulty(self, questions: List[Dict], target_difficulty: int, count: int) -> List[Dict]:
        """
        Select and adjust questions to match the target difficulty.
        
        This involves:
        1. Selecting questions that are close to the target difficulty
        2. Adjusting parameters (time limits, options) to match target difficulty
        3. Returning the specified number of questions
        """
        # First, prefer questions that already match the target difficulty
        matched_questions = [q for q in questions if q.get('difficulty_level') == target_difficulty]
        
        # If we don't have enough, include questions at adjacent difficulty levels
        if len(matched_questions) < count:
            # Add questions with difficulty +/- 1 from target
            adjacent_questions = [
                q for q in questions 
                if q.get('difficulty_level') in [target_difficulty-1, target_difficulty+1]
                and q not in matched_questions
            ]
            matched_questions.extend(adjacent_questions[:count - len(matched_questions)])
            
        # If still don't have enough, use any remaining questions
        if len(matched_questions) < count:
            remaining_questions = [q for q in questions if q not in matched_questions]
            matched_questions.extend(remaining_questions[:count - len(matched_questions)])
            
        # Limit to requested count
        selected_questions = matched_questions[:count]
        
        # Adjust each question to better match target difficulty
        for question in selected_questions:
            self._adjust_question_difficulty(question, target_difficulty)
            
        return selected_questions
        
    def _adjust_question_difficulty(self, question: Dict, target_difficulty: int) -> None:
        """
        Adjust a question's parameters to better match the target difficulty level.
        
        Modifications are made in-place to the question dictionary.
        """
        current_difficulty = question.get('difficulty_level', 3)
        
        # No adjustment needed if already at target difficulty
        if current_difficulty == target_difficulty:
            return
            
        # Set the target difficulty
        question['difficulty_level'] = target_difficulty
        question['original_difficulty'] = current_difficulty
        
        # Adjust based on question type
        question_type = question.get('type')
        
        if question_type == 'mcq':
            self._adjust_mcq_difficulty(question, target_difficulty, current_difficulty)
        elif question_type == 'fill_blank':
            self._adjust_fill_blank_difficulty(question, target_difficulty, current_difficulty)
        elif question_type == 'drag_drop':
            self._adjust_drag_drop_difficulty(question, target_difficulty, current_difficulty)
            
    def _adjust_mcq_difficulty(self, question: Dict, target_difficulty: int, current_difficulty: int) -> None:
        """Adjust multiple choice question difficulty"""
        options = question.get('options', [])
        
        if not options:
            return
            
        # Higher difficulty: Make distractors more similar to correct answer
        # Lower difficulty: Make correct answer more distinct
        
        if target_difficulty > current_difficulty:
            # Add hint for easier difficulty
            question['hint'] = "Look carefully at the details of each option."
        else:
            # Add explanation for harder questions
            if 'explanation' not in question or not question['explanation']:
                question['explanation'] = "This concept is fundamental to understanding the security principle involved."
                
    def _adjust_fill_blank_difficulty(self, question: Dict, target_difficulty: int, current_difficulty: int) -> None:
        """Adjust fill-in-the-blank question difficulty"""
        # Higher difficulty: Fewer context clues
        # Lower difficulty: More context and hints
        
        if target_difficulty < current_difficulty:
            # Add hint for easier difficulty
            question['hint'] = "The answer relates to " + question.get('content', '').split()[0]
        
    def _adjust_drag_drop_difficulty(self, question: Dict, target_difficulty: int, current_difficulty: int) -> None:
        """Adjust drag-and-drop question difficulty"""
        # Higher difficulty: More items to arrange
        # Lower difficulty: Fewer items, more context
        
        options = question.get('options', [])
        
        if not options:
            return
            
        if target_difficulty < current_difficulty:
            # Simplify by providing a hint
            question['hint'] = "Focus on the logical sequence of security controls."