from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
from app.agents.registration_agent import RegistrationAgent
from app.agents.profile_analyzer_agent import ProfileAnalyzerAgent
from app.agents.topic_mapper_agent import TopicMapperAgent
from app.agents.quiz_generator_agent import QuizGeneratorAgent
from app.agents.quiz_formatter_agent import QuizFormatterAgent
from app.agents.quiz_delivery_agent import QuizDeliveryAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.feedback_agent import FeedbackAgent
from app.agents.learning_plan_agent import LearningPlanAgent

# Initialize FastAPI app
app = FastAPI(title="Cybersecurity Quiz AI Backend")

# Enable CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define the request model that matches what Laravel is sending
class Skill(BaseModel):
    id: int
    proficiency: Optional[int] = 1

class Certification(BaseModel):
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
    skills: List[Skill] = []
    certifications: List[Certification] = []

# Define the response model
class RegistrationResponse(BaseModel):
    status: str
    quiz_id: Optional[int] = None
    quiz_title: Optional[str] = None
    complete_quiz: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# Define the registration endpoint that matches what Laravel expects
@app.post("/api/agents/register", response_model=RegistrationResponse)
async def register_user(request: RegistrationRequest):
    try:
        # Create registration agent
        registration_agent = RegistrationAgent()
        
        # Execute the registration agent with the request data
        registration_result = registration_agent._execute(request.dict())
        
        # Check if we got a user_id from registration
        if not registration_result or 'user_id' not in registration_result:
            raise HTTPException(status_code=500, detail="Failed to process registration")
        
        # Now proceed with the quiz generation process
        profile_analyzer = ProfileAnalyzerAgent()
        profile_result = profile_analyzer._execute({
            'user_id': registration_result['user_id'],
            'topic_id': request.topic_id
        })
        
        # Map topics
        topic_mapper = TopicMapperAgent()
        mapping_result = topic_mapper._execute({
            'user_id': registration_result['user_id'],
            'topic_id': request.topic_id,
            'profile_data': profile_result
        })
        
        # Generate quiz
        quiz_generator = QuizGeneratorAgent()
        quiz_content = quiz_generator._execute({
            'user_id': registration_result['user_id'],
            'topic_id': request.topic_id,
            'mapping_data': mapping_result
        })
        
        # Format quiz
        quiz_formatter = QuizFormatterAgent()
        formatted_quiz = quiz_formatter._execute({
            'user_id': registration_result['user_id'],
            'quiz_content': quiz_content
        })
        
        # Deliver quiz
        quiz_delivery = QuizDeliveryAgent()
        delivery_result = quiz_delivery._execute({
            'user_id': registration_result['user_id'],
            'formatted_quiz': formatted_quiz
        })
        
        # Return the response in the format Laravel expects
        return {
            "status": "success",
            "quiz_id": delivery_result['quiz_id'],
            "quiz_title": delivery_result.get('title', 'Cybersecurity Quiz'),
            "complete_quiz": delivery_result.get('complete_quiz', {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define an evaluation endpoint
class EvaluationRequest(BaseModel):
    user_id: int
    quiz_id: int
    responses: List[Dict[str, Any]]

class EvaluationResponse(BaseModel):
    status: str
    result_id: Optional[int] = None
    percentage_score: Optional[float] = None
    feedback: Optional[str] = None

@app.post("/api/agents/evaluate", response_model=EvaluationResponse)
async def evaluate_quiz(request: EvaluationRequest):
    try:
        # Create evaluation agent
        evaluation_agent = EvaluationAgent()
        
        # Execute the evaluation agent
        eval_result = evaluation_agent._execute({
            'user_id': request.user_id,
            'quiz_id': request.quiz_id,
            'responses': request.responses
        })
        
        if not eval_result or 'result_id' not in eval_result:
            raise HTTPException(status_code=500, detail="Failed to evaluate quiz")
        
        return {
            "status": "success",
            "result_id": eval_result['result_id'],
            "percentage_score": eval_result.get('percentage_score', 0),
            "feedback": eval_result.get('feedback', '')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define endpoint for agent operations
class AgentRequest(BaseModel):
    user_id: int
    data: Dict[str, Any]

@app.post("/api/agent/{agent_name}")
async def execute_agent(agent_name: str, request: AgentRequest):
    try:
        # Map agent names to agent classes
        agent_map = {
            'analytics_agent': AnalyticsAgent(),
            'learning_plan_agent': LearningPlanAgent(),
            'feedback_agent': FeedbackAgent()
        }
        
        if agent_name not in agent_map:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        
        # Execute the appropriate agent
        agent = agent_map[agent_name]
        result = agent._execute({
            'user_id': request.user_id,
            **request.data
        })
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)