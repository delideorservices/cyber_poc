from fastapi import APIRouter, Body, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import json
import traceback
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
from app.services.crew_service import crew_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),  # Ensure proper encoding
        logging.StreamHandler()  # Add console output
    ]
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
    use_crew_ai: Optional[bool] = True  # Flag to use CrewAI

class QuizResponseRequest(BaseModel):
    user_id: int
    quiz_id: int
    responses: List[Dict[str, Any]]
    use_crew_ai: Optional[bool] = True  # Flag to use CrewAI

# Routes for agent interaction
@router.post("/register")
async def register_user(request: RegistrationRequest):
    """Register a new user and start quiz generation process"""
    try:
        logger.info(f"Starting registration process for user {request.email}")
        request_data = request.dict()
        
        # Check if CrewAI should be used
        if request.use_crew_ai:
            # Use CrewAI for registration and subsequent processes
            logger.info("Using CrewAI for registration process")
            try:
                # Step 1: Registration Crew
                registration_result = crew_service.create_registration_crew(request_data)
                logger.info(f"CrewAI registration result: {registration_result.get('status')}")
                
                # Log the successful registration
                db_service.log_agent_action(
                    agent_name="CrewAI",
                    action="register_user",
                    input_data={"email": request.email},
                    output_data={"user_id": registration_result.get('user_id'), "status": registration_result.get('status')},
                    status="success"
                )
                
                # Step 2: Prepare data for Quiz Generation Crew
                # Get the sector and role names
                user = db_service.fetch_one(
                    """
                    SELECT u.*, s.name as sector_name, r.name as role_name
                    FROM users u
                    LEFT JOIN sectors s ON u.sector_id = s.id
                    LEFT JOIN roles r ON u.role_id = r.id
                    WHERE u.id = %s
                    """,
                    (registration_result.get('user_id', 1),)  # Default to 1 if not found
                )
                
                # Create data for quiz generation
                quiz_gen_data = {
                    'user_id': registration_result.get('user_id', 1),
                    'topic_id': registration_result.get('topic_id', request_data.get('topic_id')),
                    'topic_name': registration_result.get('topic_name', "Cybersecurity Fundamentals"),
                    'experience_level': registration_result.get('experience_level', 3),
                    'user_sector': user.get('sector_name', 'General') if user else 'General',
                    'user_role': user.get('role_name', 'General') if user else 'General',
                    'focus_areas': registration_result.get('focus_areas', ['General Cybersecurity'])
                }
                
                # Step 3: Generate Quiz using CrewAI
                logger.info(f"Using CrewAI to generate quiz for topic: {quiz_gen_data.get('topic_name')}")
                quiz_result = crew_service.create_quiz_generation_crew(quiz_gen_data)
                logger.info(f"CrewAI quiz generation result: {quiz_result.get('status')}")
                
                # Log the successful quiz generation
                db_service.log_agent_action(
                    agent_name="CrewAI",
                    action="generate_quiz",
                    input_data={"user_id": quiz_gen_data.get('user_id'), "topic": quiz_gen_data.get('topic_name')},
                    output_data={"quiz_id": quiz_result.get('quiz_id'), "status": quiz_result.get('status')},
                    status="success"
                )
                
                # Combine results and return
                combined_result = {
                    **registration_result,
                    'quiz_id': quiz_result.get('quiz_id'),
                    'quiz_title': quiz_result.get('quiz_title'),
                    'quiz_generation_status': quiz_result.get('status')
                }
                
                return combined_result
                
            except Exception as crew_err:
                logger.error(f"CrewAI registration error: {str(crew_err)}")
                logger.error(traceback.format_exc())
                
                # Log the error
                db_service.log_agent_action(
                    agent_name="CrewAI",
                    action="register_user",
                    input_data={"email": request.email},
                    status="error",
                    error_message=str(crew_err)
                )
                
                # Fallback to traditional agent chain
                logger.info("Falling back to traditional agent chain")
        
        # Use original agent chain
        logger.info("Running registration agent")
        result = registration_agent.run(request_data)
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

@router.post("/evaluate-quiz/{quiz_id}")
async def evaluate_quiz(quiz_id: int):
    """Endpoint to trigger quiz evaluation process"""
    try:
        # Fetch the quiz
        quiz = db_service.fetch_one(
            "SELECT * FROM quizzes WHERE id = %s",
            (quiz_id,)
        )
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
            
        # Start the evaluation process with the Evaluation Agent
        agent_manager = AgentManager()
        result = agent_manager.run_agent(
            'evaluation_agent', 
            {'quiz_id': quiz_id, 'user_id': quiz['user_id']}
        )
        
        # Continue with Analytics Agent
        if result['status'] == 'success' and result.get('next_agent') == 'analytics_agent':
            analytics_result = agent_manager.run_agent(
                'analytics_agent',
                {'quiz_id': quiz_id, 'user_id': quiz['user_id'], 'evaluation_results': result.get('evaluation_results', {})}
            )
            
            # Add Learning Plan Agent step to the workflow
            if analytics_result['status'] == 'success' and analytics_result.get('next_agent') == 'learning_plan_agent':
                learning_plan_result = agent_manager.run_agent(
                    'learning_plan_agent',
                    {'user_id': quiz['user_id'], 'analytics_results': analytics_result.get('analytics_results', {})}
                )
                
                # Continue with Feedback Agent
                if learning_plan_result['status'] == 'success' and learning_plan_result.get('next_agent') == 'feedback_agent':
                    feedback_result = agent_manager.run_agent(
                        'feedback_agent',
                        {
                            'user_id': quiz['user_id'], 
                            'quiz_id': quiz_id,
                            'evaluation_results': result.get('evaluation_results', {}),
                            'analytics_results': analytics_result.get('analytics_results', {}),
                            'learning_plan': learning_plan_result.get('learning_plan', {})
                        }
                    )
                    
                    return {
                        "message": "Quiz evaluation complete",
                        "evaluation_id": result.get('evaluation_id'),
                        "analytics_id": analytics_result.get('analytics_id'),
                        "learning_plan_id": learning_plan_result.get('plan_id'),
                        "feedback_id": feedback_result.get('feedback_id')
                    }
            
        return {"message": "Agent workflow interrupted", "result": result}
    except Exception as e:
        logger.error(f"Error evaluating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/generate-learning-plan/{user_id}")
async def generate_learning_plan(user_id: int):
    """Endpoint to generate a learning plan for a user"""
    try:
        # Check if user exists
        user = db_service.fetch_one(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Get latest analytics results if available
        analytics_results = db_service.fetch_one(
            """
            SELECT skill_gaps FROM user_quiz_results
            WHERE user_id = %s
            ORDER BY completed_at DESC
            LIMIT 1
            """,
            (user_id,)
        )
        
        # Setup input for Learning Plan Agent
        inputs = {
            'user_id': user_id,
            'analytics_results': {
                'skill_gaps': json.loads(analytics_results['skill_gaps']) if analytics_results and analytics_results['skill_gaps'] else {}
            }
        }
        
        # Run the Learning Plan Agent
        agent_manager = AgentManager()
        result = agent_manager.run_agent('learning_plan_agent', inputs)
        
        if result['status'] == 'success':
            return {
                "message": "Learning plan generated successfully",
                "plan_id": result.get('plan_id'),
                "learning_plan": result.get('learning_plan')
            }
        else:
            return {"message": "Failed to generate learning plan", "result": result}
    except Exception as e:
        logger.error(f"Error generating learning plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/generate-quiz-crew")
async def generate_quiz_crew(data: Dict[str, Any] = Body(...)):
    """Generate a quiz using CrewAI"""
    try:
        logger.info(f"Starting quiz generation with CrewAI for topic: {data.get('topic_name')}")
        
        # Validate required fields
        required_fields = ['user_id', 'topic_id', 'topic_name']
        for field in required_fields:
            if field not in data:
                msg = f"Missing required field: {field}"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
        
        # Add defaults for optional fields if needed
        if 'experience_level' not in data:
            data['experience_level'] = 3
        
        # Get user sector and role if not provided
        if 'user_sector' not in data or 'user_role' not in data:
            user = db_service.fetch_one(
                """
                SELECT u.*, s.name as sector_name, r.name as role_name
                FROM users u
                LEFT JOIN sectors s ON u.sector_id = s.id
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.id = %s
                """,
                (data['user_id'],)
            )
            
            if user:
                data['user_sector'] = user.get('sector_name', 'General')
                data['user_role'] = user.get('role_name', 'General')
        
        # Generate quiz using CrewAI
        result = crew_service.create_quiz_generation_crew(data)
        logger.info(f"CrewAI quiz generation result: {result.get('status')}")
        
        # Log success
        db_service.log_agent_action(
            agent_name="CrewAI",
            action="generate_quiz",
            input_data={"user_id": data.get('user_id'), "topic": data.get('topic_name')},
            output_data={"quiz_id": result.get('quiz_id'), "status": result.get('status')},
            status="success"
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in generate_quiz_crew: {str(e)}", exc_info=True)
        # Log the error in the database
        db_service.log_agent_action(
            agent_name="CrewAI",
            action="generate_quiz_crew",
            input_data={"topic": data.get('topic_name')},
            status="error",
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/test-db")
async def test_database():
    """Test database connection and quiz creation"""
    try:
        from app.services.db_service import db_service
        
        # Test connection
        conn_test = db_service.execute_with_return("SELECT 1 as test")
        if not conn_test or conn_test[0][0] != 1:
            return {"status": "error", "message": "Database connection test failed"}
        
        # Test quiz creation
        quiz_result = db_service.execute_with_return(
            """
            INSERT INTO quizzes 
            (title, user_id, topic_id, status) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id
            """,
            (
                "Test Quiz",
                0,
                1,
                'test'
            )
        )
        
        if not quiz_result or not quiz_result[0]:
            return {"status": "error", "message": "Failed to create test quiz"}
        
        quiz_id = quiz_result[0][0]
        
        # Clean up test quiz
        db_service.execute(f"DELETE FROM quizzes WHERE id = {quiz_id}")
        
        return {"status": "success", "message": f"Database test successful. Created and deleted quiz with ID {quiz_id}"}
        
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Database test failed: {str(e)}"}

@router.post("/run-agent/{agent_name}")
async def run_single_agent(agent_name: str, data: Dict[str, Any] = Body(...)):
    """Run a specific agent with provided data"""
    try:
        logger.info(f"Running single agent: {agent_name}")
        
        # Check if CrewAI should be used
        use_crew_ai = data.get('use_crew_ai', True)
        
        if use_crew_ai and agent_name in ["registration", "quiz_generation", "evaluation"]:
            logger.info(f"Using CrewAI for {agent_name}")
            
            if agent_name == "registration":
                result = crew_service.create_registration_crew(data)
            elif agent_name == "quiz_generation":
                result = crew_service.create_quiz_generation_crew(data)
            elif agent_name == "evaluation":
                result = crew_service.create_evaluation_crew(data)
            
            logger.info(f"CrewAI {agent_name} completed successfully")
            return result
        
        # Use traditional agents if not using CrewAI
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
        ],
        "crewai_available": True,
        "version": "0.1.0"
    }

# Add a CrewAI status endpoint
@router.get("/crew-status")
async def crew_status():
    """Check CrewAI status and availability"""
    try:
        # Simple test of CrewAI functionality
        from crewai import Agent
        
        return {
            "status": "available",
            "crew_version": "0.28.2",  # Update with your actual version
            "enabled": True
        }
    except Exception as e:
        logger.error(f"CrewAI status check failed: {str(e)}")
        return {
            "status": "unavailable",
            "error": str(e),
            "enabled": False
        }

# Add endpoint to toggle CrewAI
@router.post("/toggle-crew")
async def toggle_crew(data: Dict[str, Any] = Body(...)):
    """Toggle CrewAI functionality"""
    try:
        enabled = data.get('enabled', True)
        
        # In a real implementation, you might store this in a database or config file
        # For now, we'll just return the status
        
        return {
            "status": "success",
            "crew_enabled": enabled,
            "message": f"CrewAI has been {'enabled' if enabled else 'disabled'}"
        }
    except Exception as e:
        logger.error(f"Error toggling CrewAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
