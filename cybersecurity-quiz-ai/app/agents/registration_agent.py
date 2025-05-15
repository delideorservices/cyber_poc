from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.services.db_service import db_service

class RegistrationAgent(BaseAgent):
    """Agent for handling user registration and topic selection"""
    
    def __init__(self):
        super().__init__(
            name="RegistrationAgent",
            description="Handles user registration and topic input"
        )
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method required by the BaseAgent class.
        This method delegates to the _execute method.
        
        Args:
            inputs: Dictionary containing user registration data
            
        Returns:
            Dictionary with user_id and status
        """
        try:
            # Validate inputs
            if not isinstance(inputs, dict):
                raise ValueError("Inputs must be a dictionary")
            
            # Call the internal _execute method
            return self._execute(inputs)
        except Exception as e:
            # Log the error
            print(f"Error in RegistrationAgent.execute: {str(e)}")
            # Return error response
            return {
                "status": "error",
                "message": str(e)
            }

    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user registration data and store in database
        
        Args:
            inputs: Dictionary containing user registration data
            
        Returns:
            Dictionary with user_id and status
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['name', 'email', 'sector_id', 'role_id', 'topic_id'])
        
        # Check if user already exists
        existing_user = db_service.fetch_one(
            "SELECT id FROM users WHERE email = %s",
            (inputs['email'],)
        )
        
        if existing_user:
            user_id = existing_user['id']
            # Update existing user
            update_fields = []
            update_values = []
            
            for field in ['name', 'gender', 'age', 'sector_id', 'role_id', 'years_experience', 
                        'learning_goal', 'preferred_language']:
                if field in inputs:
                    update_fields.append(f"{field} = %s")
                    update_values.append(inputs[field])
            
            if update_fields:
                query = f"UPDATE users SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"
                update_values.append(user_id)
                db_service.execute(query, tuple(update_values))
        else:
            # Log attempt to create user
            print(f"Creating new user with email: {inputs['email']}")
            
            try:
                # Create new user with hashed password
                user_id = db_service.execute_returning(
                    """
                    INSERT INTO users 
                    (name, email, password, gender, age, sector_id, role_id, 
                    years_experience, learning_goal, preferred_language, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                    """,
                    (
                        inputs['name'],
                        inputs['email'],
                        inputs.get('password', ''),  # In a real app, hash this password
                        inputs.get('gender'),
                        inputs.get('age'),
                        inputs['sector_id'],
                        inputs['role_id'],
                        inputs.get('years_experience'),
                        inputs.get('learning_goal'),
                        inputs.get('preferred_language', 'en')
                    )
                )
            except Exception as e:
                # If we get a duplicate key error, try to fetch the existing user
                if "duplicate key" in str(e) and "users_email_unique" in str(e):
                    print(f"Duplicate key error, trying to fetch existing user with email: {inputs['email']}")
                    
                    existing_user = db_service.fetch_one(
                        "SELECT id FROM users WHERE email = %s",
                        (inputs['email'],)
                    )
                    
                    if existing_user:
                        user_id = existing_user['id']
                        print(f"Found existing user with ID: {user_id}")
                    else:
                        print(f"Failed to find existing user after duplicate key error")
                        raise e
                else:
                    print(f"Error creating user: {str(e)}")
                    raise e
        
        # Process skills if provided
        if 'skills' in inputs and inputs['skills']:
            # Delete existing user skills
            db_service.execute(
                "DELETE FROM user_skills WHERE user_id = %s",
                (user_id,)
            )
            
            # Add new skills
            for skill in inputs['skills']:
                skill_id = skill['id']
                proficiency = skill.get('proficiency', 1)
                
                db_service.execute(
                    """
                    INSERT INTO user_skills (user_id, skill_id, proficiency_level, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    """,
                    (user_id, skill_id, proficiency)
                )
        
        # Process certifications if provided
        if 'certifications' in inputs and inputs['certifications']:
            # Delete existing user certifications
            db_service.execute(
                "DELETE FROM user_certifications WHERE user_id = %s",
                (user_id,)
            )
            
            # Add new certifications
            for cert in inputs['certifications']:
                cert_id = cert['id']
                obtained_date = cert.get('obtained_date')
                expiry_date = cert.get('expiry_date')
                
                db_service.execute(
                    """
                    INSERT INTO user_certifications 
                    (user_id, certification_id, obtained_date, expiry_date, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                    """,
                    (user_id, cert_id, obtained_date, expiry_date)
                )
        
        # Return user_id for further processing
        return {
            'user_id': user_id,
            'topic_id': inputs['topic_id'],
            'status': 'success',
            'next_agent': 'profile_analyzer'
        }
