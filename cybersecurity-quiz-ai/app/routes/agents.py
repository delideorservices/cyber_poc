from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
from app.agents import register_agents
from app.services.db_service import DatabaseService, get_db_service

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Define request models
class UserSkill(BaseModel):
    id: int
    proficiency: Optional[int] = 1

class UserCertification(BaseModel):
    id: int
    obtained_date: Optional[str] = None
    expiry_date: Optional[str] = None

class RegistrationRequest(BaseModel):
    user_id: int
    name: str
    email: str
    gender: Optional[str] = None
    age: Optional[int] = None
    sector_id: Optional[int] = None
    role_id: Optional[int] = None
    years_experience: Optional[int] = None
    learning_goal: Optional[str] = None
    preferred_language: Optional[str] = "en"
    topic_id: int
    skills: Optional[List[UserSkill]] = []
    certifications: Optional[List[UserCertification]] = []

class EvaluationRequest(BaseModel):
    user_id: int
    quiz_id: int
    responses: List[Dict[str, Any]]

class AgentRequest(BaseModel):
    user_id: int
    data: Dict[str, Any]

# Get all available agents
agents = register_agents()

@router.post("/register")
async def register_user(request: RegistrationRequest, db: DatabaseService = Depends(get_db_service)):
    """
    Process user registration and topic selection to generate a personalized quiz
    """
    logger.info(f"Registration request for user {request.user_id} with topic {request.topic_id}")
    
    try:
        # Initialize the chain of agents
        registration_agent = agents["registration_agent"]()
        profile_analyzer = agents["profile_analyzer_agent"]()
        topic_mapper = agents["topic_mapper_agent"]()
        quiz_generator = agents["quiz_generator_agent"]()
        quiz_formatter = agents["quiz_formatter_agent"]()
        quiz_delivery = agents["quiz_delivery_agent"]()
        
        # Execute the agent chain
        registration_result = registration_agent.execute(request.dict())
        if registration_result.get("next_agent") != "profile_analyzer":
            raise HTTPException(status_code=500, detail="Registration process failed")
        
        profile_result = profile_analyzer.execute(registration_result)
        if profile_result.get("next_agent") != "topic_mapper":
            raise HTTPException(status_code=500, detail="Profile analysis failed")
        
        mapper_result = topic_mapper.execute(profile_result)
        if mapper_result.get("next_agent") != "quiz_generator":
            raise HTTPException(status_code=500, detail="Topic mapping failed")
        
        generator_result = quiz_generator.execute(mapper_result)
        if generator_result.get("next_agent") != "quiz_formatter":
            raise HTTPException(status_code=500, detail="Quiz generation failed")
        
        formatter_result = quiz_formatter.execute(generator_result)
        if formatter_result.get("next_agent") != "quiz_delivery":
            raise HTTPException(status_code=500, detail="Quiz formatting failed")
        
        delivery_result = quiz_delivery.execute(formatter_result)
        
        return {
            "status": "success",
            "quiz_id": delivery_result.get("quiz_id"),
            "quiz_title": delivery_result.get("quiz_title"),
            "complete_quiz": delivery_result.get("complete_quiz")
        }
    except Exception as e:
        logger.error(f"Error in registration process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration process failed: {str(e)}")

@router.post("/evaluate")
async def evaluate_quiz(request: EvaluationRequest, db: DatabaseService = Depends(get_db_service)):
    """
    Evaluate user's quiz responses
    """
    logger.info(f"Evaluation request for user {request.user_id}, quiz {request.quiz_id}")
    
    try:
        # Execute the evaluation agent
        evaluation_agent = agents["evaluation_agent"]()
        result = evaluation_agent.execute(request.dict())
        
        # Trigger analytics agent asynchronously
        # This is non-blocking and happens in the background
        analytics_agent = agents["analytics_agent"]()
        analytics_agent.execute_async({
            "user_id": request.user_id,
            "quiz_id": request.quiz_id,
            "result_id": result.get("result_id")
        })
        
        return {
            "status": "success",
            "result_id": result.get("result_id"),
            "percentage_score": result.get("percentage_score"),
            "feedback": result.get("feedback")
        }
    except Exception as e:
        logger.error(f"Error in quiz evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quiz evaluation failed: {str(e)}")

@router.post("/agent/{agent_name}")
async def execute_agent(agent_name: str, request: AgentRequest, db: DatabaseService = Depends(get_db_service)):
    """
    Execute a specific agent with the provided data
    """
    logger.info(f"Agent execution request: {agent_name} for user {request.user_id}")
    
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    try:
        agent_instance = agents[agent_name]()
        result = agent_instance.execute({
            "user_id": request.user_id,
            **request.data
        })
        
        return result
    except Exception as e:
        logger.error(f"Error executing agent {agent_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")