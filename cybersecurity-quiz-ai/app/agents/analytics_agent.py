import logging
from typing import Dict, Any, List, Optional
import json
import datetime
import pandas as pd
import numpy as np
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AnalyticsAgent(BaseAgent):
    """
    Analytics Agent responsible for analyzing user quiz results,
    identifying skill gaps, and generating analytical insights.
    """
    
    def __init__(self):
        """Initialize the Analytics Agent."""
        super().__init__()
        self.agent_name = "AnalyticsAgent"
    
    def execute(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Analytics Agent based on the requested action.
        
        Args:
            user_id: The user ID
            data: Additional data containing the action to perform
            
        Returns:
            Dict: The result of the analytics operation
        """
        try:
            action = data.get("action", "generate_analytics")
            
            if action == "generate_analytics":
                return self.generate_analytics(user_id)
            elif action == "get_skill_analytics":
                return self.get_skill_analytics(user_id, data.get("skill_id"))
            elif action == "get_peer_comparison":
                return self.get_peer_comparison(user_id)
            elif action == "process_quiz_results":
                return self.process_quiz_results(user_id, data.get("quiz_id"), data.get("result_id"))
            else:
                logger.error(f"Unknown action: {action}")
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.execute: {str(e)}")
            return {"error": str(e)}
    
    def generate_analytics(self, user_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive analytics for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dict: Complete analytics for the user
        """
        try:
            # Get user data
            user_data = self.get_user_data(user_id)
            
            # Get user quiz results
            quiz_results = self.get_user_quiz_results(user_id)
            
            # Get user skills
            user_skills = self.get_user_skills(user_id)
            
            # Calculate analytics
            if not quiz_results:
                logger.info(f"No quiz results found for user {user_id}")
                return {
                    "status": "success",
                    "message": "No quiz results found to generate analytics",
                    "total_quizzes": 0,
                    "avg_score": 0,
                    "strengths": [],
                    "weaknesses": []
                }
            
            # Calculate overall analytics
            total_quizzes = len(quiz_results)
            avg_score = sum(result["score"] for result in quiz_results) / total_quizzes
            
            # Process skill-specific analytics
            skill_scores = {}
            for result in quiz_results:
                # Get skill mapping from quiz result
                skill_mappings = result.get("skill_mappings", {})
                
                # Update skill scores
                for skill_id, score in skill_mappings.items():
                    if skill_id not in skill_scores:
                        skill_scores[skill_id] = []
                    skill_scores[skill_id].append(score)
            
            # Calculate average score for each skill
            skill_analytics = []
            for skill_id, scores in skill_scores.items():
                avg_skill_score = sum(scores) / len(scores)
                
                # Determine if this is a strength or weakness
                is_strength = avg_skill_score >= 80
                is_weakness = avg_skill_score <= 60
                
                # Create skill analytic record
                skill_info = next((s for s in user_skills if s["id"] == int(skill_id)), {})
                skill_name = skill_info.get("name", f"Skill #{skill_id}")
                
                skill_analytic = {
                    "user_id": user_id,
                    "skill_id": int(skill_id),
                    "skill_name": skill_name,
                    "proficiency_score": avg_skill_score,
                    "strength_level": self._calculate_strength_level(avg_skill_score),
                    "is_strength": is_strength,
                    "is_weakness": is_weakness,
                    "benchmark_percentile": self._calculate_benchmark_percentile(int(skill_id), avg_skill_score),
                    "metadata": {
                        "score_history": scores,
                        "last_updated": datetime.datetime.now().isoformat()
                    }
                }
                
                # Save to database
                existing_analytic = self.db.query_one(
                    "skill_analytics",
                    {"user_id": user_id, "skill_id": int(skill_id)}
                )
                
                if existing_analytic:
                    self.update_in_database("skill_analytics", existing_analytic["id"], skill_analytic)
                    skill_analytic["id"] = existing_analytic["id"]
                else:
                    skill_analytic_id = self.save_to_database("skill_analytics", skill_analytic)
                    skill_analytic["id"] = skill_analytic_id
                
                skill_analytics.append(skill_analytic)
            
            # Extract strengths and weaknesses
            strengths = [s for s in skill_analytics if s["is_strength"]]
            weaknesses = [s for s in skill_analytics if s["is_weakness"]]
            
            # Calculate skill domains
            skill_domains = self._calculate_skill_domains(skill_analytics)
            
            # Return analytics data
            return {
                "status": "success",
                "total_quizzes": total_quizzes,
                "avg_score": round(avg_score, 1),
                "skill_analytics": skill_analytics,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "skill_domains": skill_domains
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.generate_analytics: {str(e)}")
            return {"error": str(e)}
    
    def get_skill_analytics(self, user_id: int, skill_id: int) -> Dict[str, Any]:
        """
        Get detailed analytics for a specific skill.
        
        Args:
            user_id: The user ID
            skill_id: The skill ID
            
        Returns:
            Dict: Detailed analytics for the skill
        """
        try:
            # Get skill analytics from database
            skill_analytic = self.db.query_one(
                "skill_analytics",
                {"user_id": user_id, "skill_id": skill_id}
            )
            
            if not skill_analytic:
                logger.info(f"No analytics found for skill {skill_id} and user {user_id}")
                return {
                    "status": "success",
                    "message": "No analytics found for this skill"
                }
            
            # Get skill details
            skill_details = self.db.query_one("skills", {"id": skill_id})
            
            if not skill_details:
                skill_name = f"Skill #{skill_id}"
                skill_description = "No description available"
            else:
                skill_name = skill_details.get("name", f"Skill #{skill_id}")
                skill_description = skill_details.get("description", "No description available")
            
            # Get quiz results related to this skill
            quiz_results = self.get_user_quiz_results(user_id)
            relevant_results = []
            
            for result in quiz_results:
                skill_mappings = result.get("skill_mappings", {})
                if str(skill_id) in skill_mappings:
                    relevant_results.append({
                        "quiz_id": result["quiz_id"],
                        "quiz_title": result.get("quiz_title", "Quiz"),
                        "date": result["created_at"],
                        "score": skill_mappings[str(skill_id)]
                    })
            
            # Calculate trend data
            trend_data = []
            if relevant_results:
                # Sort by date
                relevant_results.sort(key=lambda x: x["date"])
                
                # Extract dates and scores
                dates = [result["date"] for result in relevant_results]
                scores = [result["score"] for result in relevant_results]
                
                # Create trend data
                trend_data = [{"date": date, "score": score} for date, score in zip(dates, scores)]
            
            # Get improvement suggestions
            improvement_suggestions = self._generate_improvement_suggestions(skill_id, skill_analytic["proficiency_score"])
            
            # Return detailed analytics
            detailed_analytics = {
                "status": "success",
                "skill_id": skill_id,
                "skill_name": skill_name,
                "skill_description": skill_description,
                "proficiency_score": skill_analytic["proficiency_score"],
                "strength_level": skill_analytic["strength_level"],
                "is_strength": skill_analytic["is_strength"],
                "is_weakness": skill_analytic["is_weakness"],
                "benchmark_percentile": skill_analytic["benchmark_percentile"],
                "trend_data": trend_data,
                "quiz_history": relevant_results,
                "improvement_suggestions": improvement_suggestions
            }
            
            return detailed_analytics
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.get_skill_analytics: {str(e)}")
            return {"error": str(e)}
    
    def get_peer_comparison(self, user_id: int) -> Dict[str, Any]:
        """
        Get peer comparison data for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dict: Peer comparison data
        """
        try:
            # Get user data
            user_data = self.get_user_data(user_id)
            
            if not user_data:
                logger.error(f"User data not found for user {user_id}")
                return {"error": "User data not found"}
            
            # Get user's sector and role
            sector_id = user_data.get("sector_id")
            role_id = user_data.get("role_id")
            
            # Get user's skill analytics
            user_analytics = self.db.query(
                "skill_analytics",
                {"user_id": user_id}
            )
            
            if not user_analytics:
                logger.info(f"No analytics found for user {user_id}")
                return {
                    "status": "success",
                    "message": "No analytics found for comparison"
                }
            
            # Get peer analytics (same sector and role)
            peer_analytics = self.db.query_raw(
                """
                SELECT sa.*
                FROM skill_analytics sa
                JOIN users u ON sa.user_id = u.id
                WHERE u.sector_id = %s AND u.role_id = %s AND u.id != %s
                """,
                (sector_id, role_id, user_id)
            )
            
            if not peer_analytics:
                logger.info(f"No peer analytics found for sector {sector_id} and role {role_id}")
                return {
                    "status": "success",
                    "message": "Not enough peer data for comparison",
                    "percentile": 50,  # Default to 50th percentile if no peer data
                    "domain_comparison": []
                }
            
            # Calculate domain averages
            user_domains = {}
            peer_domains = {}
            
            # Process user domain scores
            for analytic in user_analytics:
                skill_id = analytic["skill_id"]
                
                # Get skill domain
                skill = self.db.query_one("skills", {"id": skill_id})
                
                if not skill:
                    continue
                
                domain_id = skill.get("domain_id")
                
                if not domain_id:
                    continue
                
                # Get domain details
                domain = self.db.query_one("skill_domains", {"id": domain_id})
                
                if not domain:
                    continue
                
                domain_name = domain.get("name", f"Domain #{domain_id}")
                
                # Update user domain scores
                if domain_id not in user_domains:
                    user_domains[domain_id] = {
                        "id": domain_id,
                        "name": domain_name,
                        "scores": []
                    }
                
                user_domains[domain_id]["scores"].append(analytic["proficiency_score"])
            
            # Process peer domain scores
            for analytic in peer_analytics:
                skill_id = analytic["skill_id"]
                
                # Get skill domain
                skill = self.db.query_one("skills", {"id": skill_id})
                
                if not skill:
                    continue
                
                domain_id = skill.get("domain_id")
                
                if not domain_id:
                    continue
                
                # Update peer domain scores
                if domain_id not in peer_domains:
                    peer_domains[domain_id] = {
                        "scores": []
                    }
                
                peer_domains[domain_id]["scores"].append(analytic["proficiency_score"])
            
            # Calculate domain averages
            domain_comparison = []
            
            for domain_id, domain_data in user_domains.items():
                user_avg = sum(domain_data["scores"]) / len(domain_data["scores"])
                
                peer_avg = 0
                if domain_id in peer_domains and peer_domains[domain_id]["scores"]:
                    peer_avg = sum(peer_domains[domain_id]["scores"]) / len(peer_domains[domain_id]["scores"])
                
                domain_comparison.append({
                    "id": domain_id,
                    "name": domain_data["name"],
                    "user_score": round(user_avg, 1),
                    "peer_avg": round(peer_avg, 1)
                })
            
            # Calculate overall percentile
            user_overall_avg = sum(analytic["proficiency_score"] for analytic in user_analytics) / len(user_analytics)
            
            peer_scores = [
                sum(analytic["proficiency_score"] for analytic in user_peer_analytics) / len(user_peer_analytics)
                for _, user_peer_analytics in groupby(peer_analytics, key=lambda x: x["user_id"])
            ]
            
            if peer_scores:
                # Calculate percentile
                percentile = sum(1 for score in peer_scores if score < user_overall_avg) / len(peer_scores) * 100
                percentile = round(percentile)
            else:
                percentile = 50  # Default to 50th percentile if no peer scores
            
            # Return peer comparison data
            return {
                "status": "success",
                "percentile": percentile,
                "domain_comparison": domain_comparison
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.get_peer_comparison: {str(e)}")
            return {"error": str(e)}
    
    def process_quiz_results(self, user_id: int, quiz_id: int, result_id: int) -> Dict[str, Any]:
        """
        Process quiz results to update analytics.
        
        Args:
            user_id: The user ID
            quiz_id: The quiz ID
            result_id: The quiz result ID
            
        Returns:
            Dict: Result of the analytics update
        """
        try:
            # Get quiz result
            quiz_result = self.db.query_one("user_quiz_results", {"id": result_id})
            
            if not quiz_result:
                logger.error(f"Quiz result {result_id} not found")
                return {"error": "Quiz result not found"}
            
            # Generate analytics
            analytics_result = self.generate_analytics(user_id)
            
            if "error" in analytics_result:
                return analytics_result
            
            # Trigger learning plan generation if this is one of the first quizzes
            quiz_count = len(self.get_user_quiz_results(user_id))
            
            if quiz_count <= 3:
                # Import here to avoid circular import
                from .learning_plan_agent import LearningPlanAgent
                
                # Generate learning plan
                learning_plan_agent = LearningPlanAgent()
                learning_plan_result = learning_plan_agent.execute(user_id, {
                    "action": "generate_plan",
                    "quiz_id": quiz_id,
                    "result_id": result_id
                })
                
                # Return combined result
                return {
                    "status": "success",
                    "analytics_updated": True,
                    "learning_plan_generated": "error" not in learning_plan_result
                }
            
            # Return success
            return {
                "status": "success",
                "analytics_updated": True
            }
            
        except Exception as e:
            logger.exception(f"Error in {self.agent_name}.process_quiz_results: {str(e)}")
            return {"error": str(e)}
    
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
    
    def _calculate_benchmark_percentile(self, skill_id: int, score: float) -> int:
        """
        Calculate the benchmark percentile for a skill.
        
        Args:
            skill_id: The skill ID
            score: The user's score
            
        Returns:
            int: Benchmark percentile
        """
        # Get all scores for this skill
        all_analytics = self.db.query("skill_analytics", {"skill_id": skill_id})
        
        if not all_analytics:
            return 50  # Default to 50th percentile if no data
        
        # Extract scores
        all_scores = [a["proficiency_score"] for a in all_analytics]
        
        # Calculate percentile
        percentile = sum(1 for s in all_scores if s < score) / len(all_scores) * 100
        
        return round(percentile)
    
    def _calculate_skill_domains(self, skill_analytics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate skill domain averages.
        
        Args:
            skill_analytics: List of skill analytics
            
        Returns:
            List[Dict]: List of domain averages
        """
        domain_scores = {}
        
        for analytic in skill_analytics:
            skill_id = analytic["skill_id"]
            
            # Get skill domain
            skill = self.db.query_one("skills", {"id": skill_id})
            
            if not skill:
                continue
            
            domain_id = skill.get("domain_id")
            
            if not domain_id:
                continue
            
            # Get domain details
            domain = self.db.query_one("skill_domains", {"id": domain_id})
            
            if not domain:
                continue
            
            domain_name = domain.get("name", f"Domain #{domain_id}")
            
            # Update domain scores
            if domain_id not in domain_scores:
                domain_scores[domain_id] = {
                    "id": domain_id,
                    "name": domain_name,
                    "scores": []
                }
            
            domain_scores[domain_id]["scores"].append(analytic["proficiency_score"])
        
        # Calculate domain averages
        domain_averages = []
        
        for domain_id, domain_data in domain_scores.items():
            avg_score = sum(domain_data["scores"]) / len(domain_data["scores"])
            
            domain_averages.append({
                "id": domain_id,
                "name": domain_data["name"],
                "score": round(avg_score, 1)
            })
        
        return domain_averages
    
    def _generate_improvement_suggestions(self, skill_id: int, score: float) -> List[Dict[str, Any]]:
        """
        Generate improvement suggestions for a skill.
        
        Args:
            skill_id: The skill ID
            score: The proficiency score
            
        Returns:
            List[Dict]: List of improvement suggestions
        """
        # Get skill details
        skill = self.db.query_one("skills", {"id": skill_id})
        
        if not skill:
            return []
        
        skill_name = skill.get("name", f"Skill #{skill_id}")
        
        # Create agents and tasks
        analyzer_agent = self.build_crew_agent(
            name="SkillAnalyzer",
            role="Cybersecurity Skill Analyst",
            goal="Provide targeted improvement suggestions for cybersecurity skills"
        )
        
        analysis_task = self.create_task(
            agent=analyzer_agent,
            description=f"""
            Generate 3-5 practical improvement suggestions for a user with a proficiency score
            of {score} in the cybersecurity skill '{skill_name}'.
            
            For each suggestion:
            1. Provide a clear title
            2. Write a concise description of the improvement action
            3. Explain the benefit of this improvement
            4. Suggest a resource type (article, video, course, practice)
            
            Format your response as a JSON array of objects with these fields.
            """,
            expected_output="JSON array of improvement suggestions"
        )
        
        # Execute crew
        result = self.execute_crew(
            agents=[analyzer_agent],
            tasks=[analysis_task]
        )
        
        try:
            # Parse JSON result
            suggestions = json.loads(result)
            
            # Ensure correct format
            if isinstance(suggestions, list):
                return suggestions
            else:
                logger.error(f"Unexpected suggestion format: {result}")
                return []
        except Exception as e:
            logger.exception(f"Error parsing improvement suggestions: {str(e)}")
            return []