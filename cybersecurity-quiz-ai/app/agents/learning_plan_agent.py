from typing import Dict, Any, List
import json
import logging
from datetime import datetime, timedelta

from app.agents.base_agent import BaseAgent
import app.services.db_service as db_service
from app.config import LEARNING_PLAN_CONFIG
logger = logging.getLogger(__name__)

class LearningPlanAgent(BaseAgent):
    """Agent for generating personalized learning plans based on user profile and skill gaps"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "LearningPlanAgent"
        self.description = "Generates personalized cybersecurity learning plans based on skill gaps and career goals"
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized learning plan
        
        Args:
            inputs: Dictionary containing user_id and analytics_results
            
        Returns:
            Dictionary with learning plan data
        """
        # Log execution start
        logger.info("Generating learning plan for user")
        
        # Validate required inputs
        self._validate_inputs(inputs, ['user_id', 'analytics_results'])
        
        user_id = inputs['user_id']
        analytics_results = inputs['analytics_results']
        
        # Get user profile data
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
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
            
        # Extract skill gaps from analytics results
        skill_gaps = analytics_results.get('skill_gaps', {})
        if not skill_gaps:
            logger.warning("No skill gaps identified for user")
            skill_gaps = self._generate_default_skill_gaps(user)
            
        # Get user's current skills
        skills = db_service.fetch_all(
            """
            SELECT s.name, us.proficiency_level
            FROM user_skills us
            JOIN skills s ON us.skill_id = s.id
            WHERE us.user_id = %s
            """,
            (user_id,)
        )
        
        # Generate learning plan
        learning_plan = self._generate_learning_plan(user, skills, skill_gaps)
        
        # Save learning plan to database
        plan_id = self._save_learning_plan(user_id, learning_plan)
        
        # Return learning plan data
        return {
            'user_id': user_id,
            'plan_id': plan_id,
            'learning_plan': learning_plan,
            'status': 'success',
            'next_agent': 'feedback_agent'
        }
    
    def _generate_learning_plan(self, user: Dict, skills: List[Dict], skill_gaps: Dict) -> Dict:
        """
        Generate a structured learning plan based on user profile and skill gaps
        
        Args:
            user: User profile data
            skills: User's current skills with proficiency levels
            skill_gaps: Identified skill gaps from analytics
            
        Returns:
            Dictionary containing learning plan structure
        """
        # Extract user data
        experience_level = user.get('years_experience', 0)
        sector = user.get('sector_name', 'General')
        role = user.get('role_name', 'General')
        
        # Calculate appropriate plan duration based on experience and gap count
        gap_count = len(skill_gaps)
        if experience_level < 2:
            # Beginners need more time per skill
            weeks_per_skill = 3
        elif experience_level < 5:
            weeks_per_skill = 2
        else:
            # Experienced professionals can progress faster
            weeks_per_skill = 1
            
        total_duration_weeks = max(
        LEARNING_PLAN_CONFIG['min_plan_duration_weeks'], 
        min(gap_count * weeks_per_skill, LEARNING_PLAN_CONFIG['max_plan_duration_weeks'])
    )
        
        # Create plan structure
        today = datetime.now()
        end_date = today + timedelta(weeks=total_duration_weeks)
        
        # Generate a plan title
        if gap_count > 3:
            focus_area = "Comprehensive Cybersecurity"
        else:
            # Use the most critical skill gap as focus area
            focus_areas = list(skill_gaps.keys())
            focus_area = focus_areas[0] if focus_areas else "Cybersecurity"
            
        plan_title = f"{focus_area} Learning Path for {sector} {role}"
        
        # Generate learning modules for each skill gap
        modules = []
        current_start_date = today
        
        for skill_name, gap_details in skill_gaps.items():
            # Calculate module duration based on gap severity
            gap_severity = gap_details.get('severity', 3)
            module_weeks = max(1, min(gap_severity, 4))
            module_end_date = current_start_date + timedelta(weeks=module_weeks)
            
            # Determine module resources and activities
            recommended_resources = self._get_recommended_resources(skill_name, sector, role)
            practice_activities = self._generate_practice_activities(skill_name, gap_severity)
            
            # Create module structure
            module = {
                'title': f"Mastering {skill_name}",
                'description': f"Close the gap in {skill_name} with focused learning and practice",
                'skill_name': skill_name,
                'start_date': current_start_date.strftime('%Y-%m-%d'),
                'end_date': module_end_date.strftime('%Y-%m-%d'),
                'duration_weeks': module_weeks,
                'status': 'planned',
                'resources': recommended_resources,
                'activities': practice_activities,
                'assessment': {
                    'type': 'quiz',
                    'passing_score': 80,
                    'attempts_allowed': 3
                }
            }
            
            modules.append(module)
            current_start_date = module_end_date
        
        # Create complete learning plan
        learning_plan = {
            'title': plan_title,
            'description': f"Personalized learning plan focused on strengthening {gap_count} key cybersecurity skills",
            'start_date': today.strftime('%Y-%m-%d'),
            'target_end_date': end_date.strftime('%Y-%m-%d'),
            'total_duration_weeks': total_duration_weeks,
            'status': 'active',
            'skill_focus': list(skill_gaps.keys()),
            'modules': modules,
            'certification_path': self._suggest_certification_path(user, skill_gaps),
            'metadata': {
                'sector': sector,
                'role': role,
                'experience_level': experience_level,
                'generated_at': today.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return learning_plan
    
    def _save_learning_plan(self, user_id: int, learning_plan: Dict) -> int:
        """Save learning plan to database and return the plan ID"""
        # Insert learning plan record
        plan_id = db_service.execute_returning(
            """
            INSERT INTO learning_plans 
            (user_id, title, description, start_date, target_end_date, status, skill_focus, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                user_id,
                learning_plan['title'],
                learning_plan['description'],
                learning_plan['start_date'],
                learning_plan['target_end_date'],
                learning_plan['status'],
                json.dumps(learning_plan['skill_focus']),
                json.dumps(learning_plan['metadata'])
            )
        )
        
        # Insert learning modules
        for module in learning_plan['modules']:
            db_service.execute(
                """
                INSERT INTO learning_modules
                (plan_id, title, description, skill_name, start_date, end_date, 
                status, resources, activities, assessment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    plan_id,
                    module['title'],
                    module['description'],
                    module['skill_name'],
                    module['start_date'],
                    module['end_date'],
                    module['status'],
                    json.dumps(module['resources']),
                    json.dumps(module['activities']),
                    json.dumps(module['assessment'])
                )
            )
            
        return plan_id
    
    def _get_recommended_resources(self, skill_name: str, sector: str, role: str) -> List[Dict]:
        """Query database for recommended resources for a specific skill"""
        # First try to get sector and role specific resources
        resources = db_service.fetch_all(
            """
            SELECT id, title, type, url, difficulty_level
            FROM resources
            WHERE skill_tags @> %s
            AND (sector_specific @> %s OR sector_specific = '[]')
            AND (role_specific @> %s OR role_specific = '[]')
            ORDER BY relevance_score DESC
            LIMIT 5
            """,
            (
                json.dumps([skill_name]),
                json.dumps([sector]),
                json.dumps([role])
            )
        )
        
        # Format resources for output
        formatted_resources = []
        for res in resources:
            formatted_resources.append({
                'id': res['id'],
                'title': res['title'],
                'type': res['type'],
                'url': res['url'],
                'difficulty': res['difficulty_level']
            })
            
        return formatted_resources
    
    def _generate_practice_activities(self, skill_name: str, gap_severity: int) -> List[Dict]:
        """Generate practice activities based on skill and gap severity"""
        activity_types = {
            'Network Security': ['network scanning', 'firewall configuration', 'packet analysis'],
            'Encryption': ['encryption tool usage', 'key management', 'algorithm selection'],
            'Threat Analysis': ['threat hunting', 'log analysis', 'indicator identification'],
            'Incident Response': ['incident simulation', 'containment procedures', 'forensic analysis'],
            'Compliance': ['policy review', 'compliance audit', 'gap assessment'],
            'Authentication Systems': ['MFA setup', 'access control', 'identity management'],
            'Penetration Testing': ['vulnerability scanning', 'exploitation techniques', 'reporting'],
            'Security Awareness': ['social engineering simulation', 'security communication', 'awareness campaigns']
        }
        
        # Default activities if skill not found
        activities = activity_types.get(skill_name, ['research', 'practice', 'assessment'])
        
        # Determine number of activities based on gap severity
        num_activities = min(gap_severity + 1, len(activities))
        
        # Generate structured activities
        practice_activities = []
        for i in range(num_activities):
            activity_type = activities[i]
            practice_activities.append({
                'title': f"{skill_name} - {activity_type.title()}",
                'description': f"Hands-on practice with {activity_type} techniques",
                'type': 'hands-on',
                'estimated_time_minutes': 45,
                'difficulty_level': min(gap_severity, 5)
            })
            
        return practice_activities
        
    def _suggest_certification_path(self, user: Dict, skill_gaps: Dict) -> Dict:
        """Suggest relevant certifications based on user profile and skill gaps"""
        experience_level = user.get('years_experience', 0)
        sector = user.get('sector_name', 'General')
        
        # Certification paths by experience level
        certification_paths = {
            'beginner': {
                'General': ['CompTIA Security+', 'GIAC Security Essentials (GSEC)'],
                'Finance': ['CompTIA Security+', 'CISM Associate'],
                'Healthcare': ['CompTIA Security+', 'HCISPP'],
                'Technology': ['CompTIA Security+', 'CCSP Associate']
            },
            'intermediate': {
                'General': ['CISSP Associate', 'CEH', 'GIAC GCIH'],
                'Finance': ['CISM', 'CRISC', 'CISA'],
                'Healthcare': ['CISSP-ISSAP', 'HCISPP'],
                'Technology': ['CCSP', 'OSCP']
            },
            'advanced': {
                'General': ['CISSP', 'OSCP', 'GIAC GPEN'],
                'Finance': ['CISM', 'CRISC', 'CGEIT'],
                'Healthcare': ['CISSP-ISSAP', 'HCISPP', 'CISM'],
                'Technology': ['OSCP', 'CISSP', 'GIAC GSE']
            }
        }
        
        # Determine experience category
        if experience_level < 2:
            category = 'beginner'
        elif experience_level < 5:
            category = 'intermediate'
        else:
            category = 'advanced'
            
        # Get relevant certifications for sector, defaulting to General if sector not found
        sector_certs = certification_paths[category].get(sector, certification_paths[category]['General'])
        
        # Return certification recommendation
        return {
            'recommended_certifications': sector_certs[:2],
            'experience_level': category,
            'estimated_preparation_weeks': 12 if category == 'beginner' else (16 if category == 'intermediate' else 24)
        }
        
    def _generate_default_skill_gaps(self, user: Dict) -> Dict:
        """Generate default skill gaps for users with no identified gaps"""
        sector = user.get('sector_name', 'General')
        role = user.get('role_name', 'General')
        
        # Default skill gaps by sector and role
        default_gaps = {
            'Finance': {
                'Security Analyst': {'Threat Analysis': {'severity': 3}, 'Incident Response': {'severity': 2}},
                'Manager': {'Compliance': {'severity': 3}, 'Security Awareness': {'severity': 3}},
                'General': {'Security Awareness': {'severity': 3}, 'Compliance': {'severity': 2}}
            },
            'Healthcare': {
                'Security Analyst': {'Compliance': {'severity': 3}, 'Encryption': {'severity': 3}},
                'Manager': {'Compliance': {'severity': 3}, 'Security Awareness': {'severity': 3}},
                'General': {'Compliance': {'severity': 3}, 'Encryption': {'severity': 2}}
            },
            'Technology': {
                'Security Analyst': {'Penetration Testing': {'severity': 3}, 'Threat Analysis': {'severity': 2}},
                'Manager': {'Authentication Systems': {'severity': 2}, 'Network Security': {'severity': 2}},
                'General': {'Network Security': {'severity': 3}, 'Authentication Systems': {'severity': 2}}
            },
            'General': {
                'Security Analyst': {'Threat Analysis': {'severity': 3}, 'Network Security': {'severity': 2}},
                'Manager': {'Security Awareness': {'severity': 3}, 'Compliance': {'severity': 2}},
                'General': {'Security Awareness': {'severity': 3}, 'Network Security': {'severity': 2}}
            }
        }
        
        # Get default gaps for sector/role or fall back to general defaults
        sector_gaps = default_gaps.get(sector, default_gaps['General'])
        gaps = sector_gaps.get(role, sector_gaps['General'])
        
        return gaps