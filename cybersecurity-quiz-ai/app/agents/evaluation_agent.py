import json
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.db_service import db_service

class EvaluationAgent(BaseAgent):
    """Agent for evaluating user quiz responses"""
    
    def __init__(self):
        super().__init__(
            name="EvaluationAgent",
            description="Evaluates user quiz responses and calculates scores"
        )
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate user quiz responses
        
        Args:
            inputs: Dictionary containing user responses to quiz questions
            
        Returns:
            Dictionary with evaluation results
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['user_id', 'quiz_id', 'responses'])
        
        user_id = inputs['user_id']
        quiz_id = inputs['quiz_id']
        responses = inputs['responses']
        
        # Get quiz data
        quiz = db_service.fetch_one(
            "SELECT * FROM quizzes WHERE id = %s",
            (quiz_id,)
        )
        
        if not quiz:
            raise ValueError(f"Quiz with ID {quiz_id} not found")
        
        # Get all chapters in the quiz
        chapters = db_service.fetch_all(
            "SELECT * FROM chapters WHERE quiz_id = %s ORDER BY sequence",
            (quiz_id,)
        )
        
        # Initialize evaluation data
        total_points = 0
        points_earned = 0
        chapter_scores = {}
        
        # Process each chapter
        for chapter in chapters:
            chapter_id = chapter['id']
            chapter_title = chapter['title']
            
            # Get questions in this chapter
            questions = db_service.fetch_all(
                "SELECT * FROM questions WHERE chapter_id = %s ORDER BY sequence",
                (chapter_id,)
            )
            
            chapter_points = 0
            chapter_earned = 0
            
            # Process each question
            for question in questions:
                question_id = question['id']
                question_points = question['points']
                total_points += question_points
                chapter_points += question_points
                
                # Find user's response to this question
                user_response = next((r for r in responses if r.get('question_id') == question_id), None)
                
                if user_response:
                    # Check if answer is correct
                    is_correct = self._check_answer(
                        question_type=question['type'],
                        user_answer=user_response.get('answer'),
                        correct_answer=question['correct_answer']
                    )
                    
                    # Calculate points earned
                    earned_points = question_points if is_correct else 0
                    points_earned += earned_points
                    chapter_earned += earned_points
                    
                    # Save response to database
                    db_service.execute(
                        """
                        INSERT INTO user_responses
                        (user_id, question_id, response, is_correct, points_earned, answered_at, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), NOW())
                        """,
                        (
                            user_id,
                            question_id,
                            json.dumps(user_response.get('answer')),
                            is_correct,
                            earned_points
                        )
                    )
            
            # Calculate chapter score percentage
            chapter_percentage = (chapter_earned / chapter_points * 100) if chapter_points > 0 else 0
            chapter_scores[chapter_title] = {
                'points': chapter_earned,
                'total': chapter_points,
                'percentage': round(chapter_percentage, 2)
            }
        
        # Calculate overall percentage score
        percentage_score = (points_earned / total_points * 100) if total_points > 0 else 0
        
        # Identify skill gaps based on performance
        skill_gaps = self._identify_skill_gaps(chapter_scores, quiz_id)
        
        # Generate personalized feedback
        feedback = self._generate_feedback(percentage_score, chapter_scores, skill_gaps)
        
        # Save quiz result to database
        result_id = db_service.execute_returning(
            """
            INSERT INTO user_quiz_results
            (user_id, quiz_id, total_points, points_earned, percentage_score, 
             chapter_scores, skill_gaps, feedback, completed_at, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), NOW())
            RETURNING id
            """,
            (
                user_id,
                quiz_id,
                total_points,
                points_earned,
                round(percentage_score, 2),
                json.dumps(chapter_scores),
                json.dumps(skill_gaps),
                feedback
            )
        )
        
        # Return evaluation results
        return {
            'user_id': user_id,
            'quiz_id': quiz_id,
            'result_id': result_id,
            'total_points': total_points,
            'points_earned': points_earned,
            'percentage_score': round(percentage_score, 2),
            'chapter_scores': chapter_scores,
            'skill_gaps': skill_gaps,
            'feedback': feedback,
            'status': 'success',
            'next_agent': 'analytics'
        }
    
    def _check_answer(self, question_type: str, user_answer: Any, correct_answer: str) -> bool:
        """
        Check if user's answer is correct
        
        Args:
            question_type: Type of question (mcq, true_false, fill_blank)
            user_answer: User's answer
            correct_answer: Correct answer from database
            
        Returns:
            True if correct, False otherwise
        """
        # Parse correct answer from JSON string
        try:
            correct_answer = json.loads(correct_answer)
        except:
            pass
        
        # Check based on question type
        if question_type == 'mcq':
            # For MCQ, check if selected option index matches
            return str(user_answer) == str(correct_answer)
            
        elif question_type == 'true_false':
            # For True/False, compare boolean values or strings
            user_bool = user_answer.lower() if isinstance(user_answer, str) else bool(user_answer)
            correct_bool = correct_answer.lower() if isinstance(correct_answer, str) else bool(correct_answer)
            
            if isinstance(user_bool, str):
                user_bool = user_bool == 'true'
            if isinstance(correct_bool, str):
                correct_bool = correct_bool == 'true'
                
            return user_bool == correct_bool
            
        elif question_type == 'fill_blank':
            # For fill in the blank, case-insensitive comparison
            user_text = str(user_answer).lower().strip()
            correct_text = str(correct_answer).lower().strip()
            return user_text == correct_text
            
        elif question_type == 'drag_drop':
            # For drag and drop, check if arrays match
            if not isinstance(user_answer, list) or not isinstance(correct_answer, list):
                return False
            
            if len(user_answer) != len(correct_answer):
                return False
                
            return all(str(user_answer[i]) == str(correct_answer[i]) for i in range(len(user_answer)))
            
        return False
    
    def _identify_skill_gaps(self, chapter_scores: Dict, quiz_id: int) -> List[str]:
        """
        Identify skill gaps based on chapter scores
        
        Args:
            chapter_scores: Scores for each chapter
            quiz_id: ID of the quiz
            
        Returns:
            List of identified skill gaps
        """
        skill_gaps = []
        
        # Get chapters with poor performance (below 70%)
        low_performing_chapters = [
            chapter_title for chapter_title, score in chapter_scores.items()
            if score['percentage'] < 70
        ]
        
        # Map chapters to skills
        for chapter_title in low_performing_chapters:
            if 'Basics' in chapter_title:
                skill_gaps.append('Cybersecurity Fundamentals')
            elif 'Risks' in chapter_title:
                skill_gaps.append('Role-specific Security Practices')
            elif 'Threats' in chapter_title:
                skill_gaps.append('Sector-specific Security Knowledge')
            elif 'Advanced' in chapter_title:
                skill_gaps.append('Advanced Cybersecurity Concepts')
            else:
                skill_gaps.append(f"Skills related to {chapter_title}")
        
        return skill_gaps
    
    def _generate_feedback(self, percentage_score: float, chapter_scores: Dict, skill_gaps: List[str]) -> str:
        """
        Generate personalized feedback based on quiz performance
        
        Args:
            percentage_score: Overall percentage score
            chapter_scores: Scores for each chapter
            skill_gaps: Identified skill gaps
            
        Returns:
            Personalized feedback text
        """
        # Base feedback on overall score
        if percentage_score >= 90:
            overall_feedback = "Excellent work! You have a strong understanding of cybersecurity principles."
        elif percentage_score >= 80:
            overall_feedback = "Great job! You have a good grasp of cybersecurity concepts with a few areas to improve."
        elif percentage_score >= 70:
            overall_feedback = "Good effort! You understand many cybersecurity principles but have some knowledge gaps to address."
        elif percentage_score >= 60:
            overall_feedback = "You've shown basic cybersecurity knowledge, but there are important areas that need improvement."
        else:
            overall_feedback = "You need significant improvement in your cybersecurity knowledge. Focus on the basics first."
        
        # Add chapter-specific feedback
        chapter_feedback = []
        for chapter, score in chapter_scores.items():
            if score['percentage'] >= 80:
                chapter_feedback.append(f"- You performed well in {chapter} ({score['percentage']}%).")
            elif score['percentage'] >= 60:
                chapter_feedback.append(f"- You showed moderate understanding of {chapter} ({score['percentage']}%).")
            else:
                chapter_feedback.append(f"- You need to focus on improving your knowledge of {chapter} ({score['percentage']}%).")
        
        # Add skill gap recommendations
        recommendations = []
        if skill_gaps:
            for skill in skill_gaps:
                recommendations.append(f"- Review and practice {skill}.")
        else:
            recommendations.append("- Continue practicing to maintain your knowledge.")
            recommendations.append("- Consider exploring more advanced cybersecurity topics.")
        
        # Combine all feedback
        feedback = f"{overall_feedback}\n\nChapter Performance:\n"
        feedback += "\n".join(chapter_feedback)
        feedback += "\n\nRecommendations:\n"
        feedback += "\n".join(recommendations)
        
        return feedback