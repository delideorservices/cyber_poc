from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from app.agents.registration_agent import RegistrationAgent
from app.agents.profile_analyzer_agent import ProfileAnalyzerAgent
from app.agents.topic_mapper_agent import TopicMapperAgent
from app.agents.quiz_generator_agent import QuizGeneratorAgent
from app.agents.quiz_formatter_agent import QuizFormatterAgent
from app.agents.quiz_delivery_agent import QuizDeliveryAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.feedback_agent import FeedbackAgent
from app.services.db_service import db_service

# Set up logging
logging.basicConfig(
    filename='app.log',   # 👈 yahan tum log file ka naam specify kar rahe ho
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize agents
registration_agent = RegistrationAgent()
profile_analyzer_agent = ProfileAnalyzerAgent()
topic_mapper_agent = TopicMapperAgent()
quiz_generator_agent = QuizGeneratorAgent()
quiz_formatter_agent = QuizFormatterAgent()
quiz_delivery_agent = QuizDeliveryAgent()
evaluation_agent = EvaluationAgent()
analytics_agent = AnalyticsAgent()
feedback_agent = FeedbackAgent()

# Models for requests
class RegistrationRequest(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    sector_id: int
    role_id: int
    years_experience: Optional[int] = None
    learning_goal: Optional[str] = None
    preferred_language: Optional[str] = "en"
    topic_id: int
    skills: Optional[List[Dict[str, Any]]] = []
    certifications: Optional[List[Dict[str, Any]]] = []
    use_crew_ai: Optional[bool] = False  # Optional flag to use CrewAI (for future use)

class QuizResponseRequest(BaseModel):
    user_id: int
    quiz_id: int
    responses: List[Dict[str, Any]]

# Routes for agent interaction
@router.post("/register")
async def register_user(request: RegistrationRequest):
    """Register a new user and start quiz generation process"""
    try:
        logger.info(f"Starting registration process for user {request.email}")
        
        # Run registration agent
        logger.info("Running registration agent")
        result = registration_agent.run(request.dict())
        logger.info(f"Registration agent result: next_agent={result.get('next_agent')}")
        
        # Continue the agent chain
        if result.get('next_agent') == 'profile_analyzer':
            logger.info("Running profile analyzer agent")
            profile_result = profile_analyzer_agent.run(result)
            logger.info(f"Profile analyzer result: next_agent={profile_result.get('next_agent')}")
            
            if profile_result.get('next_agent') == 'topic_mapper':
                logger.info("Running topic mapper agent")
                topic_result = topic_mapper_agent.run(profile_result)
                logger.info(f"Topic mapper result: next_agent={topic_result.get('next_agent')}")
                
                if topic_result.get('next_agent') == 'quiz_generator':
                    logger.info("Running quiz generator agent")
                    quiz_result = quiz_generator_agent.run(topic_result)
                    logger.info(f"Quiz generator result: next_agent={quiz_result.get('next_agent')}, quiz_id={quiz_result.get('quiz_id')}")
                    
                    if quiz_result.get('next_agent') == 'quiz_formatter':
                        logger.info("Running quiz formatter agent")
                        format_result = quiz_formatter_agent.run(quiz_result)
                        logger.info(f"Quiz formatter result: next_agent={format_result.get('next_agent')}")
                        
                        if format_result.get('next_agent') == 'quiz_delivery':
                            logger.info("Running quiz delivery agent")
                            delivery_result = quiz_delivery_agent.run(format_result)
                            logger.info(f"Quiz delivery complete: quiz_id={delivery_result.get('quiz_id')}")
                            return delivery_result
                        
                        return format_result
                    
                    return quiz_result
                
                return topic_result
            
            return profile_result
        
        return result
    except Exception as e:
        logger.error(f"Error in register_user: {str(e)}", exc_info=True)
        # Log the error in the database
        db_service.log_agent_action(
            agent_name="api_route",
            action="register_user",
            input_data={"email": request.email},
            status="error",
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate")
async def evaluate_quiz(request: QuizResponseRequest):
    """Process user quiz responses and provide feedback"""
    try:
        logger.info(f"Starting quiz evaluation: user_id={request.user_id}, quiz_id={request.quiz_id}")
        
        # Run evaluation agent
        logger.info("Running evaluation agent")
        result = evaluation_agent.run(request.dict())
        logger.info(f"Evaluation complete: next_agent={result.get('next_agent')}")
        
        # Continue the agent chain
        if result.get('next_agent') == 'analytics':
            logger.info("Running analytics agent")
            analytics_result = analytics_agent.run(result)
            logger.info(f"Analytics complete: next_agent={analytics_result.get('next_agent')}")
            
            if analytics_result.get('next_agent') == 'feedback':
                logger.info("Running feedback agent")
                feedback_result = feedback_agent.run(analytics_result)
                logger.info("Feedback complete")
                return feedback_result
            
            return analytics_result
        
        return result
    except Exception as e:
        logger.error(f"Error in evaluate_quiz: {str(e)}", exc_info=True)
        # Log the error in the database
        db_service.log_agent_action(
            agent_name="api_route",
            action="evaluate_quiz",
            input_data={"user_id": request.user_id, "quiz_id": request.quiz_id},
            status="error",
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-agent/{agent_name}")
async def run_single_agent(agent_name: str, data: Dict[str, Any] = Body(...)):
    """Run a specific agent with provided data"""
    try:
        logger.info(f"Running single agent: {agent_name}")
        agent = None
        
        if agent_name == "registration":
            agent = registration_agent
        elif agent_name == "profile_analyzer":
            agent = profile_analyzer_agent
        elif agent_name == "topic_mapper":
            agent = topic_mapper_agent
        elif agent_name == "quiz_generator":
            agent = quiz_generator_agent
        elif agent_name == "quiz_formatter":
            agent = quiz_formatter_agent
        elif agent_name == "quiz_delivery":
            agent = quiz_delivery_agent
        elif agent_name == "evaluation":
            agent = evaluation_agent
        elif agent_name == "analytics":
            agent = analytics_agent
        elif agent_name == "feedback":
            agent = feedback_agent
        else:
            logger.warning(f"Agent '{agent_name}' not found")
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        result = agent.run(data)
        logger.info(f"Agent {agent_name} completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error running agent {agent_name}: {str(e)}", exc_info=True)
        # Log the error in the database
        db_service.log_agent_action(
            agent_name=agent_name,
            action="single_run",
            input_data=data,
            status="error",
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

# Add a health check endpoint
@router.get("/health")
async def health_check():
    """Check if the agents API is working"""
    return {
        "status": "healthy",
        "agents": [
            "registration", "profile_analyzer", "topic_mapper", 
            "quiz_generator", "quiz_formatter", "quiz_delivery",
            "evaluation", "analytics", "feedback"
        ]
    }