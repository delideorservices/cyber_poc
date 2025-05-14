import logging
from typing import Dict, Any, List, Optional
import json
import datetime
import random
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class SkillImprovementAgent(BaseAgent):
    """
    Skill Improvement Agent responsible for generating practice content,
    implementing spaced repetition, and providing targeted exercises.
    """
    
    def __init__(self):
        """Initialize the Skill Improvement Agent."""
        super().__init__()
        self.agent_name = "SkillImprovementAgent"
    
    def execute(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Skill Improvement Agent based on the requested action.
        
        Args:
            user_id: The user ID
            data: Additional data containing the action to perform
            
        Returns:
            Dict: The result of the skill improvement operation
        """
        try:
            action = data.get("action", "get_improvement_data")
            
            if action == "get_improvement_data":
                return self.get_improvement_data(user_id, data.get("skill_id"))
            elif action == "start_practice":
                return self.start_practice_session(
                    user_id, 
                    data.get("skill_id"), 
                    data.get("difficulty", 3),
                    data.get("question_count", 5)
                )
            elif action == "submit_response":
                return self.submit_practice_response(
                    user_id, 
                    data.get("practice_id"),
                    data.get("question_id"),
                    data.get("answer"),
                    data.get("time_spent")
                )
            elif action == "complete_practice":
                return self.complete_practice_session(user_id, data.get("practice_id"))
            elif action == "get_due_repetitions":
                return self.get_due_repetitions(user_id)
            elif action == "complete_repetition":
                return self.complete_repetition(
                    user_id, 
                    data.get("repetition_id"),
                    data.get("performance_rating")
                )
            else:
                logger.error(f"Unknown action: {action}")
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.execute: {str(e)}")
            return {"error": str(e)}
    
    def get_improvement_data(self, user_id: int, skill_id: int) -> Dict[str, Any]:
        """
        Get improvement data for a specific skill.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            
        Returns:
            Dict: Skill improvement data
        """
        try:
            # Get skill details
            skill = self.db.query_one("skills", {"id": skill_id})
            
            if not skill:
                logger.error(f"Skill {skill_id} not found")
                return {"error": "Skill not found"}
            
            # Get analytics for this skill
            skill_analytic = self.db.query_one(
                "skill_analytics",
                {"user_id": user_id, "skill_id": skill_id}
            )
            
            # Get practice history
            practice_sessions = self.db.query(
                "skill_practice_sessions",
                {"user_id": user_id, "skill_id": skill_id}
            )
            
            sessions_history = []
            for session in practice_sessions:
                sessions_history.append({
                    "id": session["id"],
                    "date": session["created_at"],
                    "difficulty": session["difficulty_level"],
                    "score": session["final_score"],
                    "questions_count": session["question_count"],
                    "correct_count": session["correct_count"],
                    "status": session["status"]
                })
            
            # Get improvement progress
            improvement_data = {
                "user_id": user_id,
                "skill_id": skill_id,
                "skill_name": skill["name"],
                "skill_description": skill.get("description", ""),
                "current_proficiency": skill_analytic["proficiency_score"] if skill_analytic else 0,
                "practice_history": sessions_history,
                "remaining_repetitions": self._get_repetition_count(user_id, skill_id),
                "recommended_difficulty": self._get_recommended_difficulty(user_id, skill_id),
                "progress_trend": self._get_progress_trend(user_id, skill_id)
            }
            
            # Get improvement activities
            improvement_activities = self._generate_improvement_activities(skill_id)
            improvement_data["improvement_activities"] = improvement_activities
            
            return {
                "status": "success",
                "data": improvement_data
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.get_improvement_data: {str(e)}")
            return {"error": str(e)}
    
    def start_practice_session(
        self, 
        user_id: int, 
        skill_id: int, 
        difficulty: int = 3,
        question_count: int = 5
    ) -> Dict[str, Any]:
        """
        Start a practice session for a skill.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            difficulty: The difficulty level (1-5)
            question_count: The number of questions to generate
            
        Returns:
            Dict: The created practice session with questions
        """
        try:
            # Get skill details
            skill = self.db.query_one("skills", {"id": skill_id})
            
            if not skill:
                logger.error(f"Skill {skill_id} not found")
                return {"error": "Skill not found"}
            
            # Create a new practice session
            practice_session = {
                "user_id": user_id,
                "skill_id": skill_id,
                "difficulty_level": difficulty,
                "question_count": question_count,
                "correct_count": 0,
                "final_score": 0,
                "status": "in_progress",
                "metadata": json.dumps({
                    "start_time": datetime.datetime.now().isoformat(),
                    "skill_name": skill["name"]
                })
            }
            
            # Save practice session
            session_id = self.save_to_database("skill_practice_sessions", practice_session)
            
            # Generate practice questions
            questions = self._generate_practice_questions(skill_id, difficulty, question_count)
            
            # Save questions
            for question in questions:
                question["practice_session_id"] = session_id
                question_id = self.save_to_database("practice_questions", question)
                question["id"] = question_id
            
            # Create spaced repetition records if necessary
            self._create_repetition_records(user_id, skill_id, session_id)
            
            # Return practice session with questions
            practice_session["id"] = session_id
            practice_session["questions"] = questions
            
            return {
                "status": "success",
                "practice_session": practice_session
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.start_practice_session: {str(e)}")
            return {"error": str(e)}
    
    def submit_practice_response(
        self, 
        user_id: int, 
        practice_id: int,
        question_id: int,
        answer: str,
        time_spent: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Submit a response for a practice question.
        
        Args:
            user_id: The user ID
            practice_id: The practice session ID
            question_id: The question ID
            answer: The user's answer
            time_spent: Time spent on the question in seconds
            
        Returns:
            Dict: The result of the response submission
        """
        try:
            # Get practice session
            practice_session = self.db.query_one(
                "skill_practice_sessions",
                {"id": practice_id, "user_id": user_id}
            )
            
            if not practice_session:
                logger.error(f"Practice session {practice_id} not found for user {user_id}")
                return {"error": "Practice session not found"}
            
            # Check if session is still in progress
            if practice_session["status"] != "in_progress":
                logger.error(f"Practice session {practice_id} is not in progress")
                return {"error": "Practice session is not in progress"}
            
            # Get question
            question = self.db.query_one(
                "practice_questions",
                {"id": question_id, "practice_session_id": practice_id}
            )
            
            if not question:
                logger.error(f"Question {question_id} not found for practice session {practice_id}")
                return {"error": "Question not found"}
            
            # Check if question has already been answered
            existing_response = self.db.query_one(
                "practice_responses",
                {"user_id": user_id, "question_id": question_id}
            )
            
            if existing_response:
                logger.error(f"Question {question_id} has already been answered")
                return {"error": "Question has already been answered"}
            
            # Evaluate answer
            correct_answer = question["correct_answer"]
            is_correct = self._evaluate_answer(answer, correct_answer)
            
            # Save response
            response = {
                "user_id": user_id,
                "practice_session_id": practice_id,
                "question_id": question_id,
                "answer": answer,
                "is_correct": is_correct,
                "time_spent": time_spent or 0
            }
            
            response_id = self.save_to_database("practice_responses", response)
            
            # Update practice session if correct
            if is_correct:
                practice_session["correct_count"] += 1
                self.update_in_database(
                    "skill_practice_sessions",
                    practice_id,
                    {"correct_count": practice_session["correct_count"]}
                )
            
            # Generate feedback
            feedback = self._generate_answer_feedback(question, answer, is_correct)
            
            # Return response result
            return {
                "status": "success",
                "response_id": response_id,
                "is_correct": is_correct,
                "correct_answer": correct_answer,
                "feedback": feedback
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.submit_practice_response: {str(e)}")
            return {"error": str(e)}
    
    def complete_practice_session(self, user_id: int, practice_id: int) -> Dict[str, Any]:
        """
        Complete a practice session.
        
        Args:
            user_id: The user ID
            practice_id: The practice session ID
            
        Returns:
            Dict: The result of the practice session
        """
        try:
            # Get practice session
            practice_session = self.db.query_one(
                "skill_practice_sessions",
                {"id": practice_id, "user_id": user_id}
            )
            
            if not practice_session:
                logger.error(f"Practice session {practice_id} not found for user {user_id}")
                return {"error": "Practice session not found"}
            
            # Check if session is still in progress
            if practice_session["status"] != "in_progress":
                logger.error(f"Practice session {practice_id} is not in progress")
                return {"error": "Practice session is not in progress"}
            
            # Get all questions
            questions = self.db.query(
                "practice_questions",
                {"practice_session_id": practice_id}
            )
            
            # Get all responses
            responses = self.db.query(
                "practice_responses",
                {"practice_session_id": practice_id, "user_id": user_id}
            )
            
            # Check if all questions have been answered
            if len(responses) < len(questions):
                logger.warning(f"Not all questions have been answered for practice session {practice_id}")
                # Continue anyway, but note the incomplete session
            
            # Calculate final score
            correct_count = practice_session["correct_count"]
            question_count = practice_session["question_count"]
            final_score = (correct_count / question_count) * 100 if question_count > 0 else 0
            
            # Update practice session
            self.update_in_database(
                "skill_practice_sessions",
                practice_id,
                {
                    "status": "completed",
                    "final_score": final_score,
                    "completed_at": datetime.datetime.now().isoformat()
                }
            )
            
            # Update user skill proficiency
            skill_id = practice_session["skill_id"]
            self._update_skill_proficiency(user_id, skill_id, final_score)
            
            # Get skill details
            skill = self.db.query_one("skills", {"id": skill_id})
            
            # Generate feedback
            feedback = self._generate_session_feedback(
                user_id, skill_id, correct_count, question_count, final_score
            )
            
            # Get next steps
            next_steps = self._get_next_steps(user_id, skill_id, final_score)
            
            # Return session result
            return {
                "status": "success",
                "practice_session": {
                    "id": practice_id,
                    "skill_id": skill_id,
                    "skill_name": skill["name"] if skill else f"Skill #{skill_id}",
                    "correct_count": correct_count,
                    "question_count": question_count,
                    "final_score": final_score,
                    "feedback": feedback,
                    "next_steps": next_steps
                }
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.complete_practice_session: {str(e)}")
            return {"error": str(e)}
    
    def get_due_repetitions(self, user_id: int) -> Dict[str, Any]:
        """
        Get spaced repetition items that are due for review.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dict: Due repetition items
        """
        try:
            # Get current datetime
            now = datetime.datetime.now()
            
            # Get due repetitions
            due_repetitions = self.db.query_raw(
                """
                SELECT sr.*, s.name AS skill_name
                FROM spaced_repetitions sr
                JOIN skills s ON sr.skill_id = s.id
                WHERE sr.user_id = %s AND sr.next_review_date <= %s AND sr.status = 'active'
                ORDER BY sr.next_review_date ASC
                """,
                (user_id, now.isoformat())
            )
            
            # Format due repetitions
            formatted_repetitions = []
            for rep in due_repetitions:
                formatted_repetitions.append({
                    "id": rep["id"],
                    "skill_id": rep["skill_id"],
                    "skill_name": rep["skill_name"],
                    "next_review_date": rep["next_review_date"],
                    "interval": rep["interval"],
                    "ease_factor": rep["ease_factor"],
                    "content": json.loads(rep["content"]) if rep["content"] else {}
                })
            
            return {
                "status": "success",
                "due_repetitions": formatted_repetitions,
                "count": len(formatted_repetitions)
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.get_due_repetitions: {str(e)}")
            return {"error": str(e)}
    
    def complete_repetition(
        self, 
        user_id: int, 
        repetition_id: int,
        performance_rating: int
    ) -> Dict[str, Any]:
        """
        Complete a spaced repetition item.
        
        Args:
            user_id: The user ID
            repetition_id: The repetition ID
            performance_rating: The performance rating (0-5)
            
        Returns:
            Dict: The result of the repetition completion
        """
        try:
            # Get repetition
            repetition = self.db.query_one(
                "spaced_repetitions",
                {"id": repetition_id, "user_id": user_id}
            )
            
            if not repetition:
                logger.error(f"Repetition {repetition_id} not found for user {user_id}")
                return {"error": "Repetition not found"}
            
            # Check if repetition is active
            if repetition["status"] != "active":
                logger.error(f"Repetition {repetition_id} is not active")
                return {"error": "Repetition is not active"}
            
            # Calculate new interval and ease factor using SM-2 algorithm
            interval = repetition["interval"]
            ease_factor = repetition["ease_factor"]
            
            if performance_rating < 3:
                # If rating is less than 3, reset interval
                interval = 1
            else:
                # Apply SM-2 algorithm
                if interval == 0:
                    interval = 1
                elif interval == 1:
                    interval = 6
                else:
                    interval = round(interval * ease_factor)
            
            # Adjust ease factor
            ease_factor = max(1.3, ease_factor + (0.1 - (5 - performance_rating) * 0.08))
            
            # Calculate next review date
            next_review_date = (
                datetime.datetime.now() + datetime.timedelta(days=interval)
            ).isoformat()
            
            # Update repetition
            self.update_in_database(
                "spaced_repetitions",
                repetition_id,
                {
                    "interval": interval,
                    "ease_factor": ease_factor,
                    "next_review_date": next_review_date,
                    "review_count": repetition["review_count"] + 1,
                    "last_performance_rating": performance_rating,
                    "last_review_date": datetime.datetime.now().isoformat()
                }
            )
            
            # Get updated repetition
            updated_repetition = self.db.query_one(
                "spaced_repetitions",
                {"id": repetition_id}
            )
            
            # Return updated repetition
            return {
                "status": "success",
                "repetition": {
                    "id": updated_repetition["id"],
                    "skill_id": updated_repetition["skill_id"],
                    "interval": updated_repetition["interval"],
                    "ease_factor": updated_repetition["ease_factor"],
                    "next_review_date": updated_repetition["next_review_date"],
                    "review_count": updated_repetition["review_count"]
                }
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.complete_repetition: {str(e)}")
            return {"error": str(e)}
    
    def _generate_practice_questions(
        self, 
        skill_id: int, 
        difficulty: int, 
        question_count: int
    ) -> List[Dict[str, Any]]:
        """
        Generate practice questions for a skill.
        
        Args:
            skill_id: The skill ID
            difficulty: The difficulty level (1-5)
            question_count: The number of questions to generate
            
        Returns:
            List[Dict]: Generated practice questions
        """
        # Get skill details
        skill = self.db.query_one("skills", {"id": skill_id})
        
        if not skill:
            logger.error(f"Skill {skill_id} not found")
            return []
        
        # Create agents and tasks
        question_creator_agent = self.build_crew_agent(
            name="QuestionCreator",
            role="Cybersecurity Education Expert",
            goal="Create effective practice questions for cybersecurity skills"
        )
        
        # Create question generation task
        generation_task = self.create_task(
            agent=question_creator_agent,
            description=f"""
            Create {question_count} practice questions for the cybersecurity skill: {skill['name']}
            Difficulty level: {difficulty}/5
            
            For each question:
            1. Create a clear, concise question
            2. Provide 4 possible answers (for multiple choice)
            3. Indicate the correct answer
            4. Write a brief explanation for why the answer is correct
            
            Include a mix of question types if appropriate: multiple choice, true/false, and short answer.
            
            Format your response as a JSON array of objects, each with these fields:
            - "question": the question text
            - "type": "multiple_choice", "true_false", or "short_answer"
            - "options": array of possible answers (for multiple choice)
            - "correct_answer": the correct answer
            - "explanation": explanation of the correct answer
            """,
            expected_output="JSON array of practice questions"
        )
        
        # Execute crew
        result = self.execute_crew(
            agents=[question_creator_agent],
            tasks=[generation_task]
        )
        
        try:
            # Parse JSON result
            questions_data = json.loads(result)
            
            # Format questions for database
            questions = []
            for i, q in enumerate(questions_data):
                question = {
                    "question_text": q.get("question", ""),
                    "question_type": q.get("type", "multiple_choice"),
                    "options": json.dumps(q.get("options", [])),
                    "correct_answer": q.get("correct_answer", ""),
                    "explanation": q.get("explanation", ""),
                    "difficulty_level": difficulty,
                    "sequence": i + 1
                }
                questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.exception(f"Error parsing practice questions: {str(e)}")
            
            # Return fallback questions if parsing fails
            return self._generate_fallback_questions(skill, difficulty, question_count)
    
    def _generate_fallback_questions(
        self, 
        skill: Dict[str, Any], 
        difficulty: int, 
        question_count: int
    ) -> List[Dict[str, Any]]:
        """
        Generate fallback practice questions if AI generation fails.
        
        Args:
            skill: The skill details
            difficulty: The difficulty level (1-5)
            question_count: The number of questions to generate
            
        Returns:
            List[Dict]: Generated fallback questions
        """
        questions = []
        
        # Basic question templates
        templates = [
            {
                "question": f"Which of the following best describes {skill['name']}?",
                "type": "multiple_choice",
                "options": [
                    f"A systematic approach to {skill['name']}",
                    f"A tool used primarily for {skill['name']}",
                    f"A regulatory requirement related to {skill['name']}",
                    f"A threat actor technique targeting {skill['name']}"
                ],
                "correct_answer": f"A systematic approach to {skill['name']}",
                "explanation": f"This is a basic definition of {skill['name']}."
            },
            {
                "question": f"True or False: {skill['name']} is primarily a technical control rather than an administrative control.",
                "type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "False",
                "explanation": f"{skill['name']} often involves both technical and administrative elements."
            },
            {
                "question": f"What is the primary benefit of implementing {skill['name']} in an organization?",
                "type": "multiple_choice",
                "options": [
                    "Reduced operational costs",
                    "Enhanced security posture",
                    "Improved user experience",
                    "Regulatory compliance"
                ],
                "correct_answer": "Enhanced security posture",
                "explanation": f"The main purpose of {skill['name']} is to improve security."
            },
            {
                "question": f"Which component is NOT typically associated with {skill['name']}?",
                "type": "multiple_choice",
                "options": [
                    "Risk assessment",
                    "Control implementation",
                    "Financial analysis",
                    "Security monitoring"
                ],
                "correct_answer": "Financial analysis",
                "explanation": f"While budgeting may be related, financial analysis is not a core component of {skill['name']}."
            },
            {
                "question": f"Briefly explain how {skill['name']} contributes to an organization's security program.",
                "type": "short_answer",
                "options": [],
                "correct_answer": f"{skill['name']} helps identify and mitigate security risks by providing a structured approach to security management.",
                "explanation": f"This is a fundamental concept of how {skill['name']} fits into security programs."
            }
        ]
        
        # Select a subset of templates based on question_count
        selected_templates = random.sample(templates, min(question_count, len(templates)))
        
        # Fill in remaining questions if needed
        while len(selected_templates) < question_count:
            selected_templates.append(random.choice(templates))
        
        # Format questions for database
        for i, q in enumerate(selected_templates):
            question = {
                "question_text": q["question"],
                "question_type": q["type"],
                "options": json.dumps(q["options"]),
                "correct_answer": q["correct_answer"],
                "explanation": q["explanation"],
                "difficulty_level": difficulty,
                "sequence": i + 1
            }
            questions.append(question)
        
        return questions
    
    def _evaluate_answer(self, user_answer: str, correct_answer: str) -> bool:
        """
        Evaluate if a user's answer is correct.
        
        Args:
            user_answer: The user's answer
            correct_answer: The correct answer
            
        Returns:
            bool: Whether the answer is correct
        """
        # Basic string comparison for now
        # In a real system, this would be more sophisticated
        return user_answer.strip().lower() == correct_answer.strip().lower()
    
    def _generate_answer_feedback(
        self, 
        question: Dict[str, Any], 
        user_answer: str, 
        is_correct: bool
    ) -> str:
        """
        Generate feedback for a user's answer.
        
        Args:
            question: The question details
            user_answer: The user's answer
            is_correct: Whether the answer is correct
            
        Returns:
            str: Feedback message
        """
        if is_correct:
            return f"Correct! {question['explanation']}"
        else:
            return f"Not quite. The correct answer is: {question['correct_answer']}. {question['explanation']}"
    
    def _generate_session_feedback(
        self, 
        user_id: int, 
        skill_id: int, 
        correct_count: int, 
        question_count: int, 
        final_score: float
    ) -> str:
        """
        Generate feedback for a completed practice session.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            correct_count: The number of correct answers
            question_count: The total number of questions
            final_score: The final score percentage
            
        Returns:
            str: Session feedback
        """
        # Get skill name
        skill = self.db.query_one("skills", {"id": skill_id})
        skill_name = skill["name"] if skill else f"Skill #{skill_id}"
        
        # Generate feedback based on score
        if final_score >= 90:
            return f"Excellent work! You've demonstrated a strong understanding of {skill_name} concepts. Keep up the great work and consider tackling more advanced challenges next time."
        elif final_score >= 70:
            return f"Good job! You're showing solid knowledge of {skill_name}. Review the questions you missed and practice those specific areas to improve further."
        elif final_score >= 50:
            return f"You're making progress with {skill_name}. Focus on the areas where you made mistakes, and consider reviewing the learning materials before trying again."
        else:
            return f"This topic seems challenging. Don't worry! Consider reviewing the learning materials for {skill_name} and try again with some easier practice questions."
    
    def _get_next_steps(
        self, 
        user_id: int, 
        skill_id: int, 
        final_score: float
    ) -> List[Dict[str, Any]]:
        """
        Get next steps for a user after completing a practice session.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            final_score: The final score percentage
            
        Returns:
            List[Dict]: Next steps recommendations
        """
        next_steps = []
        
        # Determine next steps based on score
        if final_score >= 90:
            # High score - suggest advanced content
            next_steps.append({
                "type": "advanced_practice",
                "title": "Try Advanced Practice",
                "description": "You're ready for more challenging content. Try an advanced practice session."
            })
            next_steps.append({
                "type": "real_world",
                "title": "Apply in Real-World Scenarios",
                "description": "Put your skills to the test in simulated real-world scenarios."
            })
        elif final_score >= 70:
            # Good score - suggest targeted practice
            next_steps.append({
                "type": "targeted_practice",
                "title": "Targeted Practice",
                "description": "Focus on specific areas you missed in this session."
            })
            next_steps.append({
                "type": "similar_difficulty",
                "title": "Similar Difficulty Practice",
                "description": "Try another practice session at the same difficulty level."
            })
        elif final_score >= 50:
            # Average score - suggest review and practice
            next_steps.append({
                "type": "review_materials",
                "title": "Review Learning Materials",
                "description": "Review the core concepts before practicing again."
            })
            next_steps.append({
                "type": "easier_practice",
                "title": "Try Easier Practice",
                "description": "Work on a slightly easier practice session to build confidence."
            })
        else:
            # Low score - suggest fundamentals
            next_steps.append({
                "type": "fundamental_review",
                "title": "Review Fundamentals",
                "description": "Take time to review the basic concepts for this skill."
            })
            next_steps.append({
                "type": "beginner_practice",
                "title": "Beginner Practice",
                "description": "Start with beginner-level practice to build your knowledge."
            })
        
        # Always suggest spaced repetition
        next_steps.append({
            "type": "spaced_repetition",
            "title": "Schedule Review",
            "description": "We'll remind you to review this material to help with retention."
        })
        
        return next_steps
    
    def _update_skill_proficiency(
        self, 
        user_id: int, 
        skill_id: int, 
        session_score: float
    ) -> None:
        """
        Update a user's skill proficiency based on practice results.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            session_score: The session score percentage
        """
        try:
            # Get current skill analytic
            skill_analytic = self.db.query_one(
                "skill_analytics",
                {"user_id": user_id, "skill_id": skill_id}
            )
            
            if not skill_analytic:
                # If no analytic exists, create one
                from .analytics_agent import AnalyticsAgent
                analytics_agent = AnalyticsAgent()
                analytics_agent.generate_analytics(user_id)
                
                # Try to get it again
                skill_analytic = self.db.query_one(
                    "skill_analytics",
                    {"user_id": user_id, "skill_id": skill_id}
                )
                
                if not skill_analytic:
                    # Still doesn't exist, create a basic one
                    skill_analytic = {
                        "user_id": user_id,
                        "skill_id": skill_id,
                        "proficiency_score": 0,
                        "strength_level": 1,
                        "is_strength": False,
                        "is_weakness": True,
                        "benchmark_percentile": 50,
                        "metadata": json.dumps({
                            "last_updated": datetime.datetime.now().isoformat()
                        })
                    }
                    
                    skill_analytic_id = self.save_to_database("skill_analytics", skill_analytic)
                    skill_analytic["id"] = skill_analytic_id
            
            # Calculate new proficiency score
            current_score = skill_analytic["proficiency_score"]
            
            # Weight the new score (30% new score, 70% current score)
            new_score = (current_score * 0.7) + (session_score * 0.3)
            
            # Determine if this is a strength or weakness
            is_strength = new_score >= 80
            is_weakness = new_score <= 60
            
            # Update skill analytic
            self.update_in_database(
                "skill_analytics",
                skill_analytic["id"],
                {
                    "proficiency_score": new_score,
                    "strength_level": self._calculate_strength_level(new_score),
                    "is_strength": is_strength,
                    "is_weakness": is_weakness,
                    "metadata": json.dumps({
                        "last_updated": datetime.datetime.now().isoformat(),
                        "last_practice_score": session_score
                    })
                }
            )
            
        except Exception as e:
            logger.exception(f"Error updating skill proficiency: {str(e)}")
    
    def _calculate_strength_level(self, score: float) -> int:
        """
        Calculate the strength level based on the score.
        
        Args:
            score: The proficiency score
            
        Returns:
            int: Strength level (1-5)
        """
        if score >= 90:
            return 5
        elif score >= 80:
            return 4
        elif score >= 70:
            return 3
        elif score >= 60:
            return 2
        else:
            return 1
    
    def _create_repetition_records(
        self, 
        user_id: int, 
        skill_id: int, 
        session_id: int
    ) -> None:
        """
        Create spaced repetition records for a practice session.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            session_id: The practice session ID
        """
        try:
            # Check if user already has repetition records for this skill
            existing_repetitions = self.db.query(
                "spaced_repetitions",
                {"user_id": user_id, "skill_id": skill_id, "status": "active"}
            )
            
            if existing_repetitions:
                # User already has repetition records
                return
            
            # Get skill details
            skill = self.db.query_one("skills", {"id": skill_id})
            
            if not skill:
                return
            
            # Get practice questions
            questions = self.db.query(
                "practice_questions",
                {"practice_session_id": session_id}
            )
            
            # Create repetition records for key concepts
            for i in range(3):  # Create 3 repetition records
                # Create content for repetition
                if i < len(questions):
                    question = questions[i]
                    content = {
                        "question": question["question_text"],
                        "answer": question["correct_answer"],
                        "explanation": question["explanation"]
                    }
                else:
                    # Create generic content if not enough questions
                    content = {
                        "concept": f"Key concept for {skill['name']}",
                        "explanation": f"Important aspect of {skill['name']} to remember"
                    }
                
                # Calculate initial review date (1 day from now)
                next_review_date = (
                    datetime.datetime.now() + datetime.timedelta(days=1)
                ).isoformat()
                
                # Create repetition record
                repetition = {
                    "user_id": user_id,
                    "skill_id": skill_id,
                    "interval": 1,  # Initial interval: 1 day
                    "ease_factor": 2.5,  # Initial ease factor: 2.5
                    "next_review_date": next_review_date,
                    "review_count": 0,
                    "last_performance_rating": 0,
                    "status": "active",
                    "content": json.dumps(content)
                }
                
                self.save_to_database("spaced_repetitions", repetition)
            
        except Exception as e:
            logger.exception(f"Error creating repetition records: {str(e)}")
    
    def _get_repetition_count(self, user_id: int, skill_id: int) -> int:
        """
        Get the number of active repetition records for a skill.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            
        Returns:
            int: Number of active repetition records
        """
        try:
            repetitions = self.db.query(
                "spaced_repetitions",
                {"user_id": user_id, "skill_id": skill_id, "status": "active"}
            )
            
            return len(repetitions)
            
        except Exception as e:
            logger.exception(f"Error getting repetition count: {str(e)}")
            return 0
    
    def _get_recommended_difficulty(self, user_id: int, skill_id: int) -> int:
        """
        Get the recommended difficulty level for a skill.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            
        Returns:
            int: Recommended difficulty level (1-5)
        """
        try:
            # Get skill analytic
            skill_analytic = self.db.query_one(
                "skill_analytics",
                {"user_id": user_id, "skill_id": skill_id}
            )
            
            if not skill_analytic:
                return 2  # Default to beginner-intermediate
            
            proficiency_score = skill_analytic["proficiency_score"]
            
            # Map proficiency score to difficulty
            if proficiency_score >= 90:
                return 5  # Expert
            elif proficiency_score >= 80:
                return 4  # Advanced
            elif proficiency_score >= 70:
                return 3  # Intermediate
            elif proficiency_score >= 50:
                return 2  # Beginner-Intermediate
            else:
                return 1  # Beginner
            
        except Exception as e:
            logger.exception(f"Error getting recommended difficulty: {str(e)}")
            return 2  # Default to beginner-intermediate
    
    def _get_progress_trend(self, user_id: int, skill_id: int) -> List[Dict[str, Any]]:
        """
        Get the progress trend for a skill.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            
        Returns:
            List[Dict]: Progress trend data
        """
        try:
            # Get practice sessions
            sessions = self.db.query_raw(
                """
                SELECT id, created_at, final_score
                FROM skill_practice_sessions
                WHERE user_id = %s AND skill_id = %s AND status = 'completed'
                ORDER BY created_at ASC
                """,
                (user_id, skill_id)
            )
            
            if not sessions:
                return []
            
            # Format trend data
            trend_data = []
            for session in sessions:
                trend_data.append({
                    "date": session["created_at"],
                    "score": session["final_score"]
                })
            
            return trend_data
            
        except Exception as e:
            logger.exception(f"Error getting progress trend: {str(e)}")
            return []
    
    def _generate_improvement_activities(self, skill_id: int) -> List[Dict[str, Any]]:
        """
        Generate improvement activities for a skill.
        
        Args:
            skill_id: The skill ID
            
        Returns:
            List[Dict]: Improvement activities
        """
        # Get skill details
        skill = self.db.query_one("skills", {"id": skill_id})
        
        if not skill:
            return []
        
        skill_name = skill["name"]
        
        # Create agents and tasks
        activity_creator_agent = self.build_crew_agent(
            name="ActivityCreator",
            role="Cybersecurity Training Designer",
            goal="Create effective improvement activities for cybersecurity skills"
        )
        
        # Create activity generation task
        generation_task = self.create_task(
            agent=activity_creator_agent,
            description=f"""
            Create 3-5 practical improvement activities for the cybersecurity skill: {skill_name}
            
            For each activity:
            1. Create a clear, actionable title
            2. Write a concise description of what the user should do
            3. Explain the benefit of this activity
            4. Estimate time required (in minutes)
            5. Indicate difficulty level (1-5)
            
            Activities should be diverse and include different types like:
            - Hands-on practice exercises
            - Research activities
            - Analysis tasks
            - Tool familiarization
            
            Format your response as a JSON array of objects with these fields.
            """,
            expected_output="JSON array of improvement activities"
        )
        
        # Execute crew
        result = self.execute_crew(
            agents=[activity_creator_agent],
            tasks=[generation_task]
        )
        
        try:
            # Parse JSON result
            activities_data = json.loads(result)
            
            # Format activities
            activities = []
            for activity in activities_data:
                activities.append({
                    "title": activity.get("title", ""),
                    "description": activity.get("description", ""),
                    "benefit": activity.get("benefit", ""),
                    "time_minutes": activity.get("time_required", 30),
                    "difficulty": activity.get("difficulty_level", 3)
                })
            
            return activities
            
        except Exception as e:
            logger.exception(f"Error parsing improvement activities: {str(e)}")
            
            # Return fallback activities if parsing fails
            return [
                {
                    "title": f"Research {skill_name} Best Practices",
                    "description": f"Find and read about current best practices for {skill_name}.",
                    "benefit": "Broadens your understanding of current industry standards",
                    "time_minutes": 45,
                    "difficulty": 2
                },
                {
                    "title": f"Hands-on {skill_name} Exercise",
                    "description": f"Complete a practical exercise related to {skill_name}.",
                    "benefit": "Builds practical experience through application",
                    "time_minutes": 60,
                    "difficulty": 3
                },
                {
                    "title": f"Analyze Real-World {skill_name} Case Study",
                    "description": f"Study a real-world case where {skill_name} was critical.",
                    "benefit": "Connects theoretical knowledge to real scenarios",
                    "time_minutes": 30,
                    "difficulty": 3
                }
            ]