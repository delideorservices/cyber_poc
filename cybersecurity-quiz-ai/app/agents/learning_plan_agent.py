import logging
from typing import Dict, Any, List, Optional
import json
import datetime
import random
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class LearningPlanAgent(BaseAgent):
    """
    Learning Plan Agent responsible for generating personalized learning plans
    based on user's skill gaps and analytics.
    """
    
    def __init__(self):
        """Initialize the Learning Plan Agent."""
        super().__init__()
        self.agent_name = "LearningPlanAgent"
    
    def execute(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Learning Plan Agent based on the requested action.
        
        Args:
            user_id: The user ID
            data: Additional data containing the action to perform
            
        Returns:
            Dict: The result of the learning plan operation
        """
        try:
            action = data.get("action", "generate_plan")
            
            if action == "generate_plan":
                return self.generate_learning_plan(user_id, data)
            elif action == "get_plan":
                return self.get_learning_plan(user_id)
            elif action == "update_plan":
                return self.update_learning_plan(user_id, data)
            else:
                logger.error(f"Unknown action: {action}")
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.execute: {str(e)}")
            return {"error": str(e)}
    
    def generate_learning_plan(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized learning plan for a user.
        
        Args:
            user_id: The user ID
            data: Additional data for plan generation
            
        Returns:
            Dict: The generated learning plan
        """
        try:
            # Get user data
            user_data = self.get_user_data(user_id)
            
            if not user_data:
                logger.error(f"User data not found for user {user_id}")
                return {"error": "User data not found"}
            
            # Get analytics data to identify skill gaps
            from .analytics_agent import AnalyticsAgent
            analytics_agent = AnalyticsAgent()
            analytics_result = analytics_agent.generate_analytics(user_id)
            
            if "error" in analytics_result:
                logger.error(f"Error generating analytics: {analytics_result['error']}")
                return {"error": f"Failed to get analytics: {analytics_result['error']}"}
            
            # Extract skill gaps (weaknesses)
            weaknesses = analytics_result.get("weaknesses", [])
            
            if not weaknesses:
                logger.info(f"No clear skill gaps found for user {user_id}")
                # If no clear weaknesses, use lowest scoring skills
                all_analytics = analytics_result.get("skill_analytics", [])
                all_analytics.sort(key=lambda x: x["proficiency_score"])
                weaknesses = all_analytics[:3] if all_analytics else []
            
            # Get user's certifications and interests
            user_certifications = self.db.query("user_certifications", {"user_id": user_id})
            
            # Check if user already has a learning plan
            existing_plan = self.db.query_one(
                "learning_plans", 
                {"user_id": user_id, "status": "active"}
            )
            
            if existing_plan:
                # Archive the existing plan
                self.update_in_database(
                    "learning_plans",
                    existing_plan["id"],
                    {"status": "archived"}
                )
            
            # Create learning plan title and description
            plan_title = self._generate_plan_title(user_data)
            plan_description = self._generate_plan_description(user_data, weaknesses)
            
            # Set target completion date (3 weeks from now)
            target_completion_date = (
                datetime.datetime.now() + datetime.timedelta(days=21)
            ).strftime("%Y-%m-%d")
            
            # Define focus areas based on weaknesses
            focus_areas = []
            for weakness in weaknesses:
                skill_name = weakness.get("skill_name", f"Skill #{weakness['skill_id']}")
                focus_areas.append({
                    "skill_id": weakness["skill_id"],
                    "skill_name": skill_name,
                    "score": weakness["proficiency_score"]
                })
            
            # Create learning plan record
            learning_plan = {
                "user_id": user_id,
                "title": plan_title,
                "description": plan_description,
                "focus_areas": json.dumps(focus_areas),
                "target_completion_date": target_completion_date,
                "status": "active",
                "difficulty_level": self._determine_difficulty_level(weaknesses),
                "overall_progress": 0,
                "metadata": json.dumps({
                    "generation_date": datetime.datetime.now().isoformat(),
                    "based_on_weaknesses": [w["skill_id"] for w in weaknesses]
                })
            }
            
            # Save learning plan to database
            learning_plan_id = self.save_to_database("learning_plans", learning_plan)
            
            # Generate learning modules
            modules = self._generate_learning_modules(
                user_id, learning_plan_id, weaknesses, user_data
            )
            
            # Save modules to database
            for module in modules:
                module["learning_plan_id"] = learning_plan_id
                module_id = self.save_to_database("learning_plan_modules", module)
                module["id"] = module_id
            
            # Return learning plan with modules
            learning_plan["id"] = learning_plan_id
            learning_plan["modules"] = modules
            
            return {
                "status": "success",
                "learning_plan": learning_plan
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.generate_learning_plan: {str(e)}")
            return {"error": str(e)}
    
    def get_learning_plan(self, user_id: int) -> Dict[str, Any]:
        """
        Get the active learning plan for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dict: The user's learning plan with modules
        """
        try:
            # Get active learning plan
            learning_plan = self.db.query_one(
                "learning_plans", 
                {"user_id": user_id, "status": "active"}
            )
            
            if not learning_plan:
                logger.info(f"No active learning plan found for user {user_id}")
                return {
                    "status": "success",
                    "message": "No active learning plan found"
                }
            
            # Get learning plan modules
            modules = self.db.query(
                "learning_plan_modules",
                {"learning_plan_id": learning_plan["id"]}
            )
            
            # Get module progress
            for module in modules:
                progress = self.db.query_one(
                    "learning_plan_progress",
                    {"user_id": user_id, "learning_plan_module_id": module["id"]}
                )
                
                if progress:
                    module["status"] = progress["status"]
                    module["progress_percentage"] = progress["progress_percentage"]
                else:
                    module["status"] = "not_started"
                    module["progress_percentage"] = 0
            
            # Sort modules by sequence
            modules.sort(key=lambda x: x["sequence"])
            
            # Add modules to learning plan
            learning_plan["modules"] = modules
            
            # Parse JSON fields
            if "focus_areas" in learning_plan and learning_plan["focus_areas"]:
                learning_plan["focus_areas"] = json.loads(learning_plan["focus_areas"])
            else:
                learning_plan["focus_areas"] = []
                
            if "metadata" in learning_plan and learning_plan["metadata"]:
                learning_plan["metadata"] = json.loads(learning_plan["metadata"])
            else:
                learning_plan["metadata"] = {}
            
            return {
                "status": "success",
                "data": learning_plan
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.get_learning_plan: {str(e)}")
            return {"error": str(e)}
    
    def update_learning_plan(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a learning plan for a user.
        
        Args:
            user_id: The user ID
            data: Update data including plan_id and updates
            
        Returns:
            Dict: Result of the update operation
        """
        try:
            plan_id = data.get("plan_id")
            updates = data.get("updates", {})
            
            if not plan_id:
                logger.error("Missing plan_id in update request")
                return {"error": "Missing plan_id"}
            
            # Get learning plan
            learning_plan = self.db.query_one(
                "learning_plans", 
                {"id": plan_id, "user_id": user_id}
            )
            
            if not learning_plan:
                logger.error(f"Learning plan {plan_id} not found for user {user_id}")
                return {"error": "Learning plan not found"}
            
            # Apply updates
            for key, value in updates.items():
                if key in ["title", "description", "status", "target_completion_date", "difficulty_level"]:
                    learning_plan[key] = value
                elif key == "focus_areas" and isinstance(value, list):
                    learning_plan["focus_areas"] = json.dumps(value)
            
            # Update learning plan
            success = self.update_in_database("learning_plans", plan_id, learning_plan)
            
            if not success:
                logger.error(f"Failed to update learning plan {plan_id}")
                return {"error": "Failed to update learning plan"}
            
            return {
                "status": "success",
                "message": "Learning plan updated successfully"
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.update_learning_plan: {str(e)}")
            return {"error": str(e)}
    
    def _generate_plan_title(self, user_data: Dict[str, Any]) -> str:
        """
        Generate a title for the learning plan.
        
        Args:
            user_data: User data
            
        Returns:
            str: Learning plan title
        """
        titles = [
            "Personalized Cybersecurity Growth Plan",
            "Targeted Security Skills Development Plan",
            "Customized Cybersecurity Learning Pathway",
            "Strategic Cybersecurity Skill Enhancement Plan",
            "Cyber Defense Capability Building Plan"
        ]
        
        return random.choice(titles)
    
    def _generate_plan_description(self, user_data: Dict[str, Any], weaknesses: List[Dict[str, Any]]) -> str:
        """
        Generate a description for the learning plan.
        
        Args:
            user_data: User data
            weaknesses: List of skill weaknesses
            
        Returns:
            str: Learning plan description
        """
        # Get user's sector and role
        sector_id = user_data.get("sector_id")
        role_id = user_data.get("role_id")
        
        sector = self.db.query_one("sectors", {"id": sector_id})
        role = self.db.query_one("roles", {"id": role_id})
        
        sector_name = sector.get("name", "your sector") if sector else "your sector"
        role_name = role.get("name", "your role") if role else "your role"
        
        # Get weakness skill names
        skill_names = []
        for weakness in weaknesses[:3]:  # Use top 3 weaknesses
            skill_names.append(weakness.get("skill_name", f"Skill #{weakness['skill_id']}"))
        
        skill_text = ""
        if skill_names:
            if len(skill_names) == 1:
                skill_text = f"focusing on {skill_names[0]}"
            elif len(skill_names) == 2:
                skill_text = f"focusing on {skill_names[0]} and {skill_names[1]}"
            else:
                skill_text = f"focusing on {', '.join(skill_names[:-1])}, and {skill_names[-1]}"
        
        # Generate description
        description = (
            f"This personalized learning plan is designed specifically for your role as a {role_name} "
            f"in the {sector_name} sector, {skill_text}. Complete the modules in sequence to build your "
            f"skills and address your specific cybersecurity knowledge gaps."
        )
        
        return description
    
    def _determine_difficulty_level(self, weaknesses: List[Dict[str, Any]]) -> int:
        """
        Determine the overall difficulty level for the learning plan.
        
        Args:
            weaknesses: List of skill weaknesses
            
        Returns:
            int: Difficulty level (1-5)
        """
        if not weaknesses:
            return 3  # Default to intermediate
        
        # Calculate average score
        avg_score = sum(w["proficiency_score"] for w in weaknesses) / len(weaknesses)
        
        # Determine difficulty based on current knowledge level
        if avg_score >= 70:
            return 4  # Advanced
        elif avg_score >= 50:
            return 3  # Intermediate
        else:
            return 2  # Beginner
    
    def _generate_learning_modules(
        self, 
        user_id: int, 
        learning_plan_id: int, 
        weaknesses: List[Dict[str, Any]],
        user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate learning modules for the learning plan.
        
        Args:
            user_id: The user ID
            learning_plan_id: The learning plan ID
            weaknesses: List of skill weaknesses
            user_data: User data
            
        Returns:
            List[Dict]: List of learning modules
        """
        modules = []
        
        # Get existing quizzes related to these skills
        skill_ids = [w["skill_id"] for w in weaknesses]
        quizzes = []
        
        for skill_id in skill_ids:
            skill_quizzes = self.db.query_raw(
                """
                SELECT q.* 
                FROM quizzes q
                JOIN quiz_skills qs ON q.id = qs.quiz_id
                WHERE qs.skill_id = %s
                LIMIT 3
                """,
                (skill_id,)
            )
            quizzes.extend(skill_quizzes)
        
        # Create agents and tasks
        module_designer_agent = self.build_crew_agent(
            name="ModuleDesigner",
            role="Cybersecurity Education Designer",
            goal="Create effective learning modules that address specific skill gaps"
        )
        
        # Create a plan for each weakness
        sequence = 1
        
        for weakness in weaknesses:
            skill_id = weakness["skill_id"]
            skill_name = weakness.get("skill_name", f"Skill #{skill_id}")
            proficiency_score = weakness["proficiency_score"]
            
            # Get skill details
            skill = self.db.query_one("skills", {"id": skill_id})
            
            if not skill:
                continue
                
            skill_description = skill.get("description", "")
            
            # Create module design task
            design_task = self.create_task(
                agent=module_designer_agent,
                description=f"""
                Design a learning module for skill: {skill_name}
                Current proficiency: {proficiency_score}/100
                Skill description: {skill_description}
                
                Create a module with:
                1. A specific, engaging title
                2. A clear description explaining what the user will learn
                3. 2-3 learning objectives
                4. Estimated hours to complete (between 1-5 hours)
                5. Appropriate difficulty level (1-5)
                
                Format your response as a JSON object with these fields.
                """,
                expected_output="JSON object with module details"
            )
            
            # Execute crew
            result = self.execute_crew(
                agents=[module_designer_agent],
                tasks=[design_task]
            )
            
            try:
                # Parse JSON result
                module_data = json.loads(result)
                
                # Extract fields
                module_title = module_data.get("title", f"Improve your {skill_name} skills")
                module_description = module_data.get("description", f"Learn essential concepts and practices to improve your {skill_name} skills.")
                module_objectives = module_data.get("learning_objectives", [])
                estimated_hours = module_data.get("estimated_hours", 3)
                difficulty_level = module_data.get("difficulty_level", 3)
                
                # Create quiz module
                quiz_module = {
                    "title": f"Quiz: {module_title}",
                    "description": f"Test your knowledge of {skill_name} concepts",
                    "module_type": "quiz",
                    "content_reference_id": self._get_or_create_quiz_for_skill(skill_id),
                    "sequence": sequence,
                    "estimated_hours": 1,
                    "difficulty_level": difficulty_level,
                    "metadata": json.dumps({
                        "skill_id": skill_id,
                        "objectives": ["Assess your current knowledge", "Identify specific areas for improvement"]
                    })
                }
                modules.append(quiz_module)
                sequence += 1
                
                # Create practice module
                practice_module = {
                    "title": f"Practice: {module_title}",
                    "description": f"Hands-on practice exercises for {skill_name}",
                    "module_type": "practice",
                    "content_reference_id": skill_id,  # Reference the skill for practice
                    "sequence": sequence,
                    "estimated_hours": estimated_hours,
                    "difficulty_level": difficulty_level,
                    "metadata": json.dumps({
                        "skill_id": skill_id,
                        "objectives": module_objectives
                    })
                }
                modules.append(practice_module)
                sequence += 1
                
                # Create resource module
                resource_module = {
                    "title": f"Resources: {module_title}",
                    "description": f"Curated resources to improve your {skill_name} skills",
                    "module_type": "resource",
                    "content_reference_id": 0,  # Will be updated with real resource ID by recommendation agent
                    "sequence": sequence,
                    "estimated_hours": 2,
                    "difficulty_level": difficulty_level,
                    "metadata": json.dumps({
                        "skill_id": skill_id,
                        "objectives": ["Deepen your understanding", "Learn from experts in the field"]
                    })
                }
                modules.append(resource_module)
                sequence += 1
                
            except Exception as e:
                logger.exception(f"Error processing module design result: {str(e)}")
                continue
        
        # Add assessment module at the end
        assessment_module = {
            "title": "Final Assessment",
            "description": "Test your overall progress and improvement across all focus areas",
            "module_type": "assessment",
            "content_reference_id": 0,  # Placeholder, will be created when user reaches this stage
            "sequence": sequence,
            "estimated_hours": 1,
            "difficulty_level": 3,
            "metadata": json.dumps({
                "skill_ids": skill_ids,
                "objectives": ["Assess overall improvement", "Identify remaining areas for future focus"]
            })
        }
        modules.append(assessment_module)
        
        return modules
    
    def _get_or_create_quiz_for_skill(self, skill_id: int) -> int:
        """
        Get an existing quiz for a skill or create a placeholder.
        
        Args:
            skill_id: The skill ID
            
        Returns:
            int: Quiz ID
        """
        # Try to find an existing quiz for this skill
        quiz_skill = self.db.query_one("quiz_skills", {"skill_id": skill_id})
        
        if quiz_skill:
            return quiz_skill["quiz_id"]
        
        # If no quiz exists, create a placeholder
        # In a real implementation, we would trigger quiz generation
        skill = self.db.query_one("skills", {"id": skill_id})
        skill_name = skill.get("name", f"Skill #{skill_id}") if skill else f"Skill #{skill_id}"
        
        quiz = {
            "title": f"{skill_name} Assessment",
            "description": f"Assessment quiz for {skill_name}",
            "user_id": 1,  # System user
            "topic_id": 1,  # Default topic
            "difficulty_level": 3
        }
        
        quiz_id = self.save_to_database("quizzes", quiz)
        
        # Associate the quiz with the skill
        quiz_skill = {
            "quiz_id": quiz_id,
            "skill_id": skill_id,
            "relevance_score": 100  # Maximum relevance
        }
        
        self.save_to_database("quiz_skills", quiz_skill)
        
        return quiz_id