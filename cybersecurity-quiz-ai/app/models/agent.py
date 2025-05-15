from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import date

# Base model for skills
class SkillInput(BaseModel):
    id: int
    proficiency: Optional[int] = 1

# Certification model
class CertificationInput(BaseModel):
    id: int
    obtained_date: Optional[date] = None
    expiry_date: Optional[date] = None

# Main registration request model
class RegistrationRequest(BaseModel):
    user_id: int
    name: str
    email: str
    gender: Optional[str] = None
    age: Optional[int] = None
    sector_id: int
    role_id: int
    years_experience: Optional[int] = None
    learning_goal: Optional[str] = None
    preferred_language: Optional[str] = "en"
    topic_id: int
    skills: List[SkillInput] = []
    certifications: List[CertificationInput] = []

# Model for quiz evaluation
class QuizResponse(BaseModel):
    question_id: int
    answer: Any

class EvaluationRequest(BaseModel):
    user_id: int
    quiz_id: int
    responses: List[QuizResponse]

# Agent request model (for direct agent execution)
class AgentRequest(BaseModel):
    user_id: int
    data: Dict[str, Any]

# Response models
class RegistrationResponse(BaseModel):
    status: str
    quiz_id: Optional[int] = None
    quiz_title: Optional[str] = None
    complete_quiz: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class EvaluationResponse(BaseModel):
    status: str
    result_id: Optional[str] = None
    percentage_score: Optional[float] = None
    feedback: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None