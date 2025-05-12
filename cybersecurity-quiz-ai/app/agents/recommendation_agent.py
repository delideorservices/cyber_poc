from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
import app.services.db_service as db_service
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class RecommendationAgent(BaseAgent):
    """Agent for generating personalized learning resource recommendations"""

    def __init__(self):
        super().__init__(
            name="RecommendationAgent",
            description="Generates personalized learning resource recommendations based on user skill gaps"
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized recommendations based on user skill gaps

        Args:
            inputs: Dictionary containing user_id and skill_gaps

        Returns:
            Dictionary with recommended resources
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['user_id', 'skill_gaps'])

        user_id = inputs['user_id']
        skill_gaps = inputs['skill_gaps']

        # Get user profile data
        user = self._get_user_profile(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Get available learning resources
        resources = self._get_learning_resources()

        # Match resources to skill gaps
        recommendations = self._match_resources_to_skill_gaps(user, resources, skill_gaps)

        # Store recommendations in database
        self._store_recommendations(user_id, recommendations)

        return {
            'user_id': user_id,
            'recommendations': recommendations,
            'status': 'success',
            'next_agent': 'none' # This is the final agent in the workflow
        }

    def _get_user_profile(self, user_id):
        """Fetch user profile with preferences and quiz history"""
        user = db_service.fetch_one(
            """
            SELECT u.*, s.name as sector_name, r.name as role_name
            FROM users u
            LEFT JOIN sectors s ON u.sector_id = s.id
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
            """,
            (user_id,)
        )

        # Get user completed quizzes
        completed_quizzes = db_service.fetch_all(
            """
            SELECT uqr.*, q.topic_id
            FROM user_quiz_results uqr
            JOIN quizzes q ON uqr.quiz_id = q.id
            WHERE uqr.user_id = %s
            """,
            (user_id,)
        )

        if user:
            user['completed_quizzes'] = completed_quizzes
            return user
        return None

    def _get_learning_resources(self):
        """Fetch all learning resources from the database"""
        return db_service.fetch_all(
            """
            SELECT * FROM learning_resources
            """
        )

    def _match_resources_to_skill_gaps(self, user, resources, skill_gaps):
        """
        Core recommendation algorithm: Match learning resources to user's skill gaps
        """
        # Extract user attributes for personalization
        sector_id = user.get('sector_id')
        role_id = user.get('role_id')
        experience_level = user.get('years_experience', 0)
        preferred_difficulty = min(max(int(experience_level / 2) + 1, 1), 5)

        # Calculate relevance for each resource
        recommendations = []
        already_recommended_ids = self._get_already_recommended_resource_ids(user['id'])

        for resource in resources:
            # Skip if already recommended
            if resource['id'] in already_recommended_ids:
                continue

            # Parse skill tags and topic tags
            resource_skill_tags = json.loads(resource['skill_tags'])
            relevance_score = 0
            targeted_skills = []

            # Calculate skill relevance - this is the core matching algorithm
            for gap in skill_gaps:
                skill_id = gap.get('skill_id')
                proficiency = gap.get('current_proficiency', 0)
                target = gap.get('target_proficiency', 5)
                gap_size = target - proficiency

                # If this resource helps with this skill
                if skill_id in resource_skill_tags:
                    targeted_skills.append(skill_id)
                    # Calculate a relevance score (0-100)
                    skill_relevance = min(gap_size * 20, 100) # Scale gap size to 0-100
                    relevance_score += skill_relevance

            # Skip if resource doesn't target any skill gaps
            if not targeted_skills:
                continue

            # Adjust relevance based on difficulty match
            difficulty_match = 1.0 - (abs(preferred_difficulty - resource['difficulty_level']) * 0.1)
            relevance_score *= max(difficulty_match, 0.5)

            # Boost relevance for sector-specific resources if applicable
            if sector_id and resource['sector_id'] == sector_id:
                relevance_score *= 1.25 # 25% boost for sector-specific content

            # Normalize final score to 0-100 range
            relevance_score = min(relevance_score / len(targeted_skills), 100)

            # Generate recommendation reason
            reason = self._generate_recommendation_reason(resource, targeted_skills, skill_gaps)

            # Add to recommendations list if relevance score is high enough
            if relevance_score > 30: # Only recommend if relevance is above threshold
                recommendations.append({
                    'resource_id': resource['id'],
                    'title': resource['title'],
                    'description': resource['description'],
                    'url': resource['url'],
                    'resource_type': resource['resource_type'],
                    'difficulty_level': resource['difficulty_level'],
                    'estimated_minutes': resource['estimated_minutes'],
                    'relevance_score': round(relevance_score, 2),
                    'targeted_skills': targeted_skills,
                    'recommendation_reason': reason
                })

        # Sort recommendations by relevance score (highest first)
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)

        # Limit to top 5 recommendations
        return recommendations[:5]

    def _generate_recommendation_reason(self, resource, targeted_skills, skill_gaps):
        """Generate a personalized reason for this recommendation"""
        # Get skill names for targeted skills
        skill_names = []
        for skill_id in targeted_skills:
            for gap in skill_gaps:
                if gap.get('skill_id') == skill_id and 'skill_name' in gap:
                    skill_names.append(gap['skill_name'])

        # Generate reason based on resource type and skills
        if skill_names:
            skills_text = ", ".join(skill_names[:-1]) + (" and " + skill_names[-1] if len(skill_names) > 1 else skill_names[0])
            resource_type = resource['resource_type'].lower()

            # Different messages based on resource type
            if resource_type == 'article':
                return f"This article will help you improve your {skills_text} skills."
            elif resource_type == 'video':
                return f"This video tutorial is recommended to strengthen your understanding of {skills_text}."
            elif resource_type == 'course':
                return f"This course will provide comprehensive training on {skills_text}."
            elif resource_type == 'exercise':
                return f"This hands-on exercise will help you practice and improve your {skills_text} skills."
            else:
                return f"This resource is recommended to help you develop your {skills_text} skills."
        else:
            return "This resource is recommended based on your learning needs."

    def _get_already_recommended_resource_ids(self, user_id):
        """Get IDs of resources already recommended to this user"""
        recommendations = db_service.fetch_all(
            """
            SELECT learning_resource_id FROM recommendations
            WHERE user_id = %s
            """,
            (user_id,)
        )
        return [r['learning_resource_id'] for r in recommendations]

    def _store_recommendations(self, user_id, recommendations):
        """Store recommendations in the database"""
        for rec in recommendations:
            db_service.execute_returning(
                """
                INSERT INTO recommendations
                (user_id, learning_resource_id, relevance_score, targeted_skills, recommendation_reason, recommended_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                RETURNING id
                """,
                (
                    user_id,
                    rec['resource_id'],
                    rec['relevance_score'],
                    json.dumps(rec['targeted_skills']),
                    rec['recommendation_reason']
                )
            )
        logger.info(f"Stored {len(recommendations)} recommendations for user {user_id}")