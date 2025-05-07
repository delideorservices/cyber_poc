from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.db_service import db_service

class ProfileAnalyzerAgent(BaseAgent):
    """Agent for analyzing user profile to determine appropriate quiz content"""
    
    def __init__(self):
        super().__init__(
            name="ProfileAnalyzerAgent",
            description="Analyzes user profile to determine quiz difficulty and content focus"
        )
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user profile data to determine quiz parameters
        
        Args:
            inputs: Dictionary containing user_id from previous step
            
        Returns:
            Dictionary with profile analysis results
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['user_id'])
        
        user_id = inputs['user_id']
        
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
        
        # Get user skills
        skills = db_service.fetch_all(
            """
            SELECT s.name, us.proficiency_level
            FROM user_skills us
            JOIN skills s ON us.skill_id = s.id
            WHERE us.user_id = %s
            """,
            (user_id,)
        )
        
        # Get user certifications
        certifications = db_service.fetch_all(
            """
            SELECT c.name, c.provider
            FROM user_certifications uc
            JOIN certifications c ON uc.certification_id = c.id
            WHERE uc.user_id = %s
            """,
            (user_id,)
        )
        
        # Calculate experience level (1-5)
        experience_level = self._calculate_experience_level(
            years_experience=user.get('years_experience', 0),
            skills=skills,
            certifications=certifications
        )
        
        # Determine area focus based on role and sector
        focus_areas = self._determine_focus_areas(
            sector=user.get('sector_name'),
            role=user.get('role_name'),
            skills=skills
        )
        
        analysis_results = {
            'user_id': user_id,
            'topic_id': inputs['topic_id'],
            'experience_level': experience_level,
            'focus_areas': focus_areas,
            'sector': user.get('sector_name'),
            'role': user.get('role_name'),
            'status': 'success',
            'next_agent': 'topic_mapper'
        }
        
        return analysis_results
    
    def _calculate_experience_level(self, years_experience: int, 
                                   skills: List[Dict], 
                                   certifications: List[Dict]) -> int:
        """
        Calculate user's experience level on a scale of 1-5
        
        Args:
            years_experience: Years of experience
            skills: List of user skills with proficiency levels
            certifications: List of user certifications
            
        Returns:
            Experience level (1-5)
        """
        # Base score from years of experience
        if years_experience <= 1:
            base_score = 1
        elif years_experience <= 3:
            base_score = 2
        elif years_experience <= 5:
            base_score = 3
        elif years_experience <= 10:
            base_score = 4
        else:
            base_score = 5
        
        # Add points for skills proficiency (average)
        skill_points = 0
        if skills:
            skill_avg = sum(s.get('proficiency_level', 1) for s in skills) / len(skills)
            skill_points = skill_avg / 5  # Normalize to 0-1 range
        
        # Add points for certifications
        cert_points = min(len(certifications) * 0.5, 1.0)  # Max 1 point from certs
        
        # Calculate final score (weighted average)
        final_score = (base_score * 0.5) + (skill_points * 0.3) + (cert_points * 0.2)
        
        # Round to nearest integer and ensure within 1-5 range
        return max(1, min(5, round(final_score)))
    
    def _determine_focus_areas(self, sector: str, role: str, skills: List[Dict]) -> List[str]:
        """
        Determine areas to focus on based on user's role, sector, and skills
        
        Args:
            sector: User's sector
            role: User's role
            skills: List of user skills
            
        Returns:
            List of focus areas
        """
        focus_areas = []
        
        # Add sector-specific focus areas
        if sector == 'Banking':
            focus_areas.extend(['Financial Fraud', 'Customer Data Protection'])
        elif sector == 'Healthcare':
            focus_areas.extend(['Patient Privacy', 'Medical Data Security'])
        elif sector == 'Travel':
            focus_areas.extend(['Booking Systems Security', 'Customer Data Protection'])
        elif sector == 'Finance':
            focus_areas.extend(['Financial Data Security', 'Transaction Security'])
        
        # Add role-specific focus areas
        if role:
            if 'Manager' in role or 'Administrator' in role:
                focus_areas.append('Management Security Responsibilities')
            elif 'Advisor' in role or 'Consultant' in role:
                focus_areas.append('Client Data Protection')
            elif 'Teller' in role or 'Agent' in role:
                focus_areas.append('Front-line Security Awareness')
        
        # Add general focus areas
        focus_areas.append('General Cybersecurity Awareness')
        
        return focus_areas