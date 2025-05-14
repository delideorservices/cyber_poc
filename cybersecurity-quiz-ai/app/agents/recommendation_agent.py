
import os
import logging
from typing import Dict, List, Any, Optional
import random
import json
from datetime import datetime

import pandas as pd
import numpy as np
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING', 
                                'postgresql://postgres:postgres@db:5432/cybersecurity_quiz')
engine = create_engine(DB_CONNECTION_STRING)

class RecommendationAgent:
    """
    Agent responsible for generating personalized resource recommendations
    based on user's profile, skill gaps, and learning preferences.
    """
    
    def __init__(self):
        """Initialize the RecommendationAgent with required models and data."""
        # Initialize language model
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name=os.getenv('OPENAI_MODEL_NAME', 'gpt-4'),
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize recommendation prompt template
        self.recommendation_template = PromptTemplate(
            input_variables=["user_profile", "skill_gaps", "learning_style", "previous_resources"],
            template="""
            You are an expert cybersecurity learning advisor. Based on the following information,
            recommend 5 personalized learning resources for the user.
            
            User Profile:
            {user_profile}
            
            Skill Gaps:
            {skill_gaps}
            
            Learning Style Preferences:
            {learning_style}
            
            Previously Recommended Resources:
            {previous_resources}
            
            For each recommendation, provide:
            1. Title
            2. Description
            3. Resource Type (article, video, interactive exercise, etc.)
            4. Difficulty Level (1-5)
            5. Estimated Time to Complete (in minutes)
            6. Primary Skill Addressed
            7. Relevance Score (1-10)
            8. Learning Style Match (how it matches their preferred learning style)
            9. URL or Reference
            
            Format as JSON array.
            """
        )
        
        # Initialize recommendation chain
        self.recommendation_chain = LLMChain(
            llm=self.llm,
            prompt=self.recommendation_template
        )
        
    def execute(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the recommendation agent based on the action requested.
        
        Args:
            user_id (int): The ID of the user
            data (Dict[str, Any]): Request data containing action and parameters
            
        Returns:
            Dict[str, Any]: Response containing recommendations or status
        """
        action = data.get('action')
        
        if action == 'generate_recommendations':
            return self._generate_recommendations(user_id, data)
        elif action == 'process_feedback':
            return self._process_feedback(user_id, data)
        else:
            return {
                'status': 'error',
                'message': f'Unknown action: {action}'
            }
            
    def _generate_recommendations(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized recommendations for the user.
        
        Args:
            user_id (int): The ID of the user
            data (Dict[str, Any]): Request data containing filters
            
        Returns:
            Dict[str, Any]: Response containing recommendations
        """
        try:
            # Get request parameters
            count = data.get('count', 5)
            resource_type = data.get('type')
            
            # Get user profile information
            user_profile = self._get_user_profile(user_id)
            if not user_profile:
                return {'status': 'error', 'message': 'User profile not found'}
                
            # Get user's skill gaps
            skill_gaps = self._get_user_skill_gaps(user_id)
            
            # Get user's learning style preferences
            learning_style = self._get_user_learning_style(user_id)
            
            # Get previously recommended resources
            previous_resources = self._get_previous_recommendations(user_id)
            
            # Generate recommendations using LLM
            recommendations = self._run_recommendation_chain(
                user_profile, 
                skill_gaps, 
                learning_style, 
                previous_resources
            )
            
            # Filter by resource type if specified
            if resource_type:
                recommendations = [r for r in recommendations if r.get('resource_type', '').lower() == resource_type.lower()]
            
            # Limit to requested count
            recommendations = recommendations[:count]
            
            # Add recommendations to database
            saved_recommendations = self._save_recommendations(user_id, recommendations)
            
            return {
                'status': 'success',
                'recommendations': saved_recommendations,
                'count': len(saved_recommendations)
            }
            
        except Exception as e:
            logger.exception(f"Error generating recommendations: {e}")
            return {
                'status': 'error',
                'message': f'Failed to generate recommendations: {str(e)}'
            }
            
    def _process_feedback(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback for a recommendation to improve future suggestions.
        
        Args:
            user_id (int): The ID of the user
            data (Dict[str, Any]): Feedback data
            
        Returns:
            Dict[str, Any]: Response indicating success or failure
        """
        try:
            recommendation_id = data.get('recommendation_id')
            rating = data.get('rating')
            feedback = data.get('feedback')
            
            if not recommendation_id:
                return {'status': 'error', 'message': 'Recommendation ID is required'}
                
            # Log feedback for future model improvement
            with Session(engine) as session:
                # Update recommendation record with feedback
                query = text("""
                    UPDATE resource_recommendations
                    SET user_rating = :rating, 
                        user_feedback = :feedback,
                        updated_at = NOW()
                    WHERE id = :recommendation_id AND user_id = :user_id
                    RETURNING id
                """)
                
                result = session.execute(
                    query, 
                    {
                        'recommendation_id': recommendation_id,
                        'user_id': user_id,
                        'rating': rating,
                        'feedback': feedback
                    }
                )
                
                session.commit()
                
                updated_id = result.fetchone()
                if not updated_id:
                    return {'status': 'error', 'message': 'Recommendation not found or not authorized'}
            
            # Get user's learning style preferences and update based on feedback
            if rating and rating >= 4:
                self._update_learning_preferences(user_id, recommendation_id)
            
            return {
                'status': 'success',
                'message': 'Feedback processed successfully'
            }
            
        except Exception as e:
            logger.exception(f"Error processing feedback: {e}")
            return {
                'status': 'error',
                'message': f'Failed to process feedback: {str(e)}'
            }
    
    def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Fetch user profile information from the database."""
        with Session(engine) as session:
            query = text("""
                SELECT u.id, u.name, u.email, u.years_experience, u.learning_goal,
                       s.name as sector_name, r.name as role_name
                FROM users u
                LEFT JOIN sectors s ON u.sector_id = s.id
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.id = :user_id
            """)
            
            result = session.execute(query, {'user_id': user_id}).fetchone()
            
            if not result:
                return {}
                
            # Get user's skills
            skills_query = text("""
                SELECT s.name, us.proficiency_level
                FROM user_skills us
                JOIN skills s ON us.skill_id = s.id
                WHERE us.user_id = :user_id
            """)
            
            skills = session.execute(skills_query, {'user_id': user_id}).fetchall()
            
            # Get user's certifications
            cert_query = text("""
                SELECT c.name, uc.obtained_date
                FROM user_certifications uc
                JOIN certifications c ON uc.certification_id = c.id
                WHERE uc.user_id = :user_id
            """)
            
            certifications = session.execute(cert_query, {'user_id': user_id}).fetchall()
            
            # Format the profile
            return {
                'id': result.id,
                'name': result.name,
                'email': result.email,
                'sector': result.sector_name,
                'role': result.role_name,
                'years_experience': result.years_experience,
                'learning_goal': result.learning_goal,
                'skills': [{'name': s.name, 'level': s.proficiency_level} for s in skills],
                'certifications': [{'name': c.name, 'obtained_date': c.obtained_date} for c in certifications]
            }
    
    def _get_user_skill_gaps(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch user's skill gaps from analytics data."""
        with Session(engine) as session:
            query = text("""
                SELECT sa.id, s.name, sa.proficiency_score, sa.is_weakness, 
                       sa.benchmark_percentile, sa.metadata
                FROM skill_analytics sa
                JOIN skills s ON sa.skill_id = s.id
                WHERE sa.user_id = :user_id AND sa.is_weakness = true
                ORDER BY sa.proficiency_score ASC
                LIMIT 5
            """)
            
            results = session.execute(query, {'user_id': user_id}).fetchall()
            
            skill_gaps = []
            for row in results:
                metadata = row.metadata if row.metadata else {}
                skill_gap = {
                    'skill_id': row.id,
                    'name': row.name,
                    'proficiency_score': row.proficiency_score,
                    'benchmark_percentile': row.benchmark_percentile,
                }
                
                # Add any additional metadata
                if isinstance(metadata, dict):
                    for key, value in metadata.items():
                        if key not in skill_gap:
                            skill_gap[key] = value
                            
                skill_gaps.append(skill_gap)
                
            # If no skill gaps found from analytics, use quiz results
            if not skill_gaps:
                # Get recent quiz results to identify potential skill gaps
                quiz_query = text("""
                    SELECT qr.id, q.topic_id, t.name as topic_name, qr.score,
                           qr.metadata
                    FROM user_quiz_results qr
                    JOIN quizzes q ON qr.quiz_id = q.id
                    JOIN topics t ON q.topic_id = t.id
                    WHERE qr.user_id = :user_id
                    ORDER BY qr.created_at DESC
                    LIMIT 3
                """)
                
                quiz_results = session.execute(quiz_query, {'user_id': user_id}).fetchall()
                
                for row in quiz_results:
                    if row.score < 70:  # Consider topics with scores below 70% as skill gaps
                        skill_gaps.append({
                            'name': row.topic_name,
                            'proficiency_score': row.score,
                            'source': 'quiz_result',
                            'quiz_id': row.id
                        })
                        
            return skill_gaps
    
    def _get_user_learning_style(self, user_id: int) -> Dict[str, Any]:
        """Fetch user's learning style preferences."""
        with Session(engine) as session:
            # First check if we have explicitly stored preferences
            query = text("""
                SELECT preferences
                FROM user_preferences
                WHERE user_id = :user_id AND preference_type = 'learning_style'
            """)
            
            result = session.execute(query, {'user_id': user_id}).fetchone()
            
            if result and result.preferences:
                return result.preferences
                
            # If not, infer from past resource interactions
            interaction_query = text("""
                SELECT r.resource_type, rr.user_rating, COUNT(*) as interaction_count
                FROM resource_recommendations rr
                JOIN resources r ON rr.resource_id = r.id
                WHERE rr.user_id = :user_id AND rr.user_rating IS NOT NULL
                GROUP BY r.resource_type, rr.user_rating
                ORDER BY rr.user_rating DESC, interaction_count DESC
            """)
            
            interactions = session.execute(interaction_query, {'user_id': user_id}).fetchall()
            
            # Default preferences if no data available
            learning_style = {
                'preferred_formats': ['video', 'article', 'interactive'],
                'session_duration': 'medium',  # short, medium, long
                'complexity_level': 'intermediate',  # beginner, intermediate, advanced
                'interaction_preference': 'active'  # passive, active
            }
            
            # Update based on interactions
            if interactions:
                # Calculate preferred formats based on highest ratings
                format_ratings = {}
                for row in interactions:
                    resource_type = row.resource_type
                    rating = row.user_rating
                    if resource_type not in format_ratings:
                        format_ratings[resource_type] = {'sum': 0, 'count': 0}
                    format_ratings[resource_type]['sum'] += rating
                    format_ratings[resource_type]['count'] += 1
                
                # Calculate average rating for each format
                for resource_type, data in format_ratings.items():
                    format_ratings[resource_type]['avg'] = data['sum'] / data['count']
                
                # Sort by average rating
                sorted_formats = sorted(
                    format_ratings.items(), 
                    key=lambda x: x[1]['avg'], 
                    reverse=True
                )
                
                # Update preferred formats with top 3
                if sorted_formats:
                    learning_style['preferred_formats'] = [f[0] for f in sorted_formats[:3]]
            
            return learning_style
            
    def _get_previous_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch previously recommended resources for the user."""
        with Session(engine) as session:
            query = text("""
                SELECT r.id, r.title, r.description, r.resource_type,
                       r.difficulty_level, r.url, rr.status, rr.user_rating
                FROM resource_recommendations rr
                JOIN resources r ON rr.resource_id = r.id
                WHERE rr.user_id = :user_id
                ORDER BY rr.created_at DESC
                LIMIT 10
            """)
            
            results = session.execute(query, {'user_id': user_id}).fetchall()
            
            return [
                {
                    'id': row.id,
                    'title': row.title,
                    'description': row.description,
                    'resource_type': row.resource_type,
                    'difficulty_level': row.difficulty_level,
                    'url': row.url,
                    'status': row.status,
                    'user_rating': row.user_rating
                }
                for row in results
            ]
            
    def _run_recommendation_chain(
        self, 
        user_profile: Dict[str, Any], 
        skill_gaps: List[Dict[str, Any]], 
        learning_style: Dict[str, Any],
        previous_resources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Run the LLM recommendation chain to generate personalized recommendations."""
        try:
            # Format inputs for the prompt
            user_profile_str = json.dumps(user_profile, indent=2)
            skill_gaps_str = json.dumps(skill_gaps, indent=2)
            learning_style_str = json.dumps(learning_style, indent=2)
            previous_resources_str = json.dumps(previous_resources, indent=2)
            
            # Run the chain
            response = self.recommendation_chain.run({
                "user_profile": user_profile_str,
                "skill_gaps": skill_gaps_str,
                "learning_style": learning_style_str,
                "previous_resources": previous_resources_str
            })
            
            # Parse the JSON response
            try:
                recommendations = json.loads(response)
                if not isinstance(recommendations, list):
                    recommendations = [recommendations]
            except json.JSONDecodeError:
                logger.error(f"Failed to parse recommendation response as JSON: {response}")
                # If parsing fails, attempt to extract JSON from the response
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    try:
                        recommendations = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        recommendations = []
                else:
                    recommendations = []
            
            # Format and sanitize recommendations
            formatted_recommendations = []
            for rec in recommendations:
                formatted_rec = {
                    'title': rec.get('Title', 'Untitled Resource'),
                    'description': rec.get('Description', ''),
                    'resource_type': rec.get('Resource Type', 'article').lower(),
                    'difficulty_level': min(max(int(rec.get('Difficulty Level', 3)), 1), 5),
                    'estimated_minutes': int(rec.get('Estimated Time to Complete', 30)),
                    'primary_skill': rec.get('Primary Skill Addressed', ''),
                    'relevance_score': min(max(int(rec.get('Relevance Score', 5)), 1), 10),
                    'learning_style_match': rec.get('Learning Style Match', ''),
                    'url': rec.get('URL or Reference', '')
                }
                formatted_recommendations.append(formatted_rec)
                
            return formatted_recommendations
            
        except Exception as e:
            logger.exception(f"Error in recommendation chain: {e}")
            # Fallback to generic recommendations if LLM fails
            return self._generate_fallback_recommendations(skill_gaps, learning_style)
            
    def _generate_fallback_recommendations(
        self, 
        skill_gaps: List[Dict[str, Any]], 
        learning_style: Dict[str, Any]   ) -> List[Dict[str, Any]]:
        """Generate fallback recommendations when the LLM chain fails."""
        fallback_recommendations = []
        
        # Map of cybersecurity topics to resource templates
        resource_templates = {
            'network': [
                {
                    'title': 'Network Security Fundamentals',
                    'description': 'Learn the basics of securing computer networks',
                    'resource_type': 'course',
                    'difficulty_level': 2,
                    'estimated_minutes': 120,
                    'url': 'https://www.cybrary.it/course/network-security-fundamentals/'
                },
                {
                    'title': 'Advanced Firewall Configuration Guide',
                    'description': 'Step-by-step guide for configuring enterprise firewalls',
                    'resource_type': 'article',
                    'difficulty_level': 4,
                    'estimated_minutes': 45,
                    'url': 'https://www.sans.org/reading-room/whitepapers/firewalls/'
                }
            ],
            'cryptography': [
                {
                    'title': 'Practical Cryptography for Developers',
                    'description': 'Hands-on guide to implementing cryptographic protocols',
                    'resource_type': 'interactive',
                    'difficulty_level': 3,
                    'estimated_minutes': 90,
                    'url': 'https://cryptobook.nakov.com/'
                }
            ],
            'web': [
                {
                    'title': 'OWASP Top 10 Web Vulnerabilities',
                    'description': 'Comprehensive guide to the most critical web security risks',
                    'resource_type': 'article',
                    'difficulty_level': 3,
                    'estimated_minutes': 60,
                    'url': 'https://owasp.org/www-project-top-ten/'
                }
            ],
            'cloud': [
                {
                    'title': 'Cloud Security Best Practices',
                    'description': 'Learn how to secure cloud environments and applications',
                    'resource_type': 'video',
                    'difficulty_level': 3,
                    'estimated_minutes': 75,
                    'url': 'https://www.youtube.com/watch?v=QD5mpOe3Hj4'
                }
            ],
            'malware': [
                {
                    'title': 'Malware Analysis Fundamentals',
                    'description': 'Introduction to analyzing and understanding malicious software',
                    'resource_type': 'course',
                    'difficulty_level': 4,
                    'estimated_minutes': 180,
                    'url': 'https://academy.tcm-sec.com/p/practical-malware-analysis-triage'
                }
            ]
        }
        
        # Get preferred resource types
        preferred_formats = learning_style.get('preferred_formats', ['article', 'video', 'course'])
        
        # Generate recommendations based on skill gaps
        for skill_gap in skill_gaps:
            skill_name = skill_gap.get('name', '').lower()
            
            # Find matching topic
            matching_topic = None
            for topic in resource_templates.keys():
                if topic in skill_name:
                    matching_topic = topic
                    break
                    
            if matching_topic:
                # Get resources for the matching topic
                topic_resources = resource_templates[matching_topic]
                
                # Filter by preferred format if possible
                matching_resources = [r for r in topic_resources 
                                     if r['resource_type'] in preferred_formats]
                
                # If no matches with preferred format, use all resources for the topic
                if not matching_resources:
                    matching_resources = topic_resources
                    
                # Take the first matching resource
                if matching_resources:
                    resource = matching_resources[0].copy()
                    resource['primary_skill'] = skill_name
                    resource['relevance_score'] = 8
                    resource['learning_style_match'] = f"Matches your preferred {resource['resource_type']} format"
                    fallback_recommendations.append(resource)
                    
        # If still not enough recommendations, add general cybersecurity resources
        general_resources = [
            {
                'title': 'Cybersecurity Fundamentals',
                'description': 'Introduction to key cybersecurity concepts and principles',
                'resource_type': 'course',
                'difficulty_level': 1,
                'estimated_minutes': 240,
                'primary_skill': 'cybersecurity basics',
                'relevance_score': 7,
                'learning_style_match': 'Comprehensive introduction for all learning styles',
                'url': 'https://www.coursera.org/learn/cybersecurity-basics'
            },
            {
                'title': 'Practical Security Measures for Small Businesses',
                'description': 'Actionable security practices to protect small business assets',
                'resource_type': 'article',
                'difficulty_level': 2,
                'estimated_minutes': 30,
                'primary_skill': 'practical security',
                'relevance_score': 6,
                'learning_style_match': 'Quick practical guide for busy professionals',
                'url': 'https://www.cisa.gov/small-business-resources'
            }
        ]
        
        # Add general resources until we have at least 5 recommendations
        while len(fallback_recommendations) < 5 and general_resources:
            fallback_recommendations.append(general_resources.pop(0))
            
        return fallback_recommendations
            
    def _save_recommendations(
        self, 
        user_id: int, 
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Save recommendations to the database and return saved items."""
        with Session(engine) as session:
            saved_recommendations = []
            
            for rec in recommendations:
                # Check if resource already exists
                resource_query = text("""
                    SELECT id FROM resources 
                    WHERE title = :title AND url = :url
                """)
                
                resource_result = session.execute(
                    resource_query, 
                    {'title': rec['title'], 'url': rec['url']}
                ).fetchone()
                
                if resource_result:
                    resource_id = resource_result.id
                else:
                    # Create new resource
                    resource_insert = text("""
                        INSERT INTO resources 
                        (title, description, resource_type, difficulty_level, 
                         estimated_minutes, url, metadata, created_at, updated_at)
                        VALUES
                        (:title, :description, :resource_type, :difficulty_level,
                         :estimated_minutes, :url, :metadata, NOW(), NOW())
                        RETURNING id
                    """)
                    
                    metadata = {
                        'primary_skill': rec.get('primary_skill'),
                        'relevance_score': rec.get('relevance_score'),
                        'learning_style_match': rec.get('learning_style_match')
                    }
                    
                    resource_id_result = session.execute(
                        resource_insert,
                        {
                            'title': rec['title'],
                            'description': rec['description'],
                            'resource_type': rec['resource_type'],
                            'difficulty_level': rec['difficulty_level'],
                            'estimated_minutes': rec['estimated_minutes'],
                            'url': rec['url'],
                            'metadata': json.dumps(metadata)
                        }
                    ).fetchone()
                    
                    resource_id = resource_id_result.id
                
                # Create recommendation record
                rec_insert = text("""
                    INSERT INTO resource_recommendations
                    (user_id, resource_id, status, relevance_score, created_at, updated_at)
                    VALUES
                    (:user_id, :resource_id, 'new', :relevance_score, NOW(), NOW())
                    RETURNING id
                """)
                
                rec_id_result = session.execute(
                    rec_insert,
                    {
                        'user_id': user_id,
                        'resource_id': resource_id,
                        'relevance_score': rec.get('relevance_score', 5)
                    }
                ).fetchone()
                
                # Add to results
                saved_rec = rec.copy()
                saved_rec['id'] = rec_id_result.id
                saved_rec['resource_id'] = resource_id
                saved_rec['status'] = 'new'
                saved_recommendations.append(saved_rec)
                
            session.commit()
            return saved_recommendations
            
    def _update_learning_preferences(self, user_id: int, recommendation_id: int) -> None:
        """Update user learning style preferences based on positive feedback."""
        with Session(engine) as session:
            # Get the resource type for the recommendation
            query = text("""
                SELECT r.resource_type
                FROM resource_recommendations rr
                JOIN resources r ON rr.resource_id = r.id
                WHERE rr.id = :recommendation_id
            """)
            
            result = session.execute(query, {'recommendation_id': recommendation_id}).fetchone()
            if not result:
                return
                
            resource_type = result.resource_type
            
            # Get or create user preferences
            pref_query = text("""
                SELECT id, preferences
                FROM user_preferences
                WHERE user_id = :user_id AND preference_type = 'learning_style'
            """)
            
            pref_result = session.execute(pref_query, {'user_id': user_id}).fetchone()
            
            if pref_result:
                # Update existing preferences
                pref_id = pref_result.id
                preferences = pref_result.preferences if pref_result.preferences else {}
                
                # Update preferred formats if needed
                if 'preferred_formats' in preferences:
                    formats = preferences['preferred_formats']
                    # Move the resource type to the front if it exists
                    if resource_type in formats:
                        formats.remove(resource_type)
                    formats.insert(0, resource_type)
                    preferences['preferred_formats'] = formats[:5]  # Keep top 5
                else:
                    preferences['preferred_formats'] = [resource_type]
                
                # Update preferences
                update_query = text("""
                    UPDATE user_preferences
                    SET preferences = :preferences, updated_at = NOW()
                    WHERE id = :id
                """)
                
                session.execute(
                    update_query, 
                    {'id': pref_id, 'preferences': json.dumps(preferences)}
                )
                
            else:
                # Create new preferences
                preferences = {
                    'preferred_formats': [resource_type],
                    'session_duration': 'medium',
                    'complexity_level': 'intermediate',
                    'interaction_preference': 'active'
                }
                
                insert_query = text("""
                    INSERT INTO user_preferences
                    (user_id, preference_type, preferences, created_at, updated_at)
                    VALUES
                    (:user_id, 'learning_style', :preferences, NOW(), NOW())
                """)
                
                session.execute(
                    insert_query,
                    {'user_id': user_id, 'preferences': json.dumps(preferences)}
                )
                
            session.commit()

# For testing purposes
if __name__ == "__main__":
    # Create a simple test function
    def test_recommendation_agent():
        agent = RecommendationAgent()
        
        # Mock user data
        user_id = 1
        data = {
            'action': 'generate_recommendations',
            'count': 3
        }
        
        # Test the agent
        result = agent.execute(user_id, data)
        print(json.dumps(result, indent=2))