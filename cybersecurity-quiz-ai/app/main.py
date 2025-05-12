import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.agents.skill_improvement_agent import SkillImprovementAgent
from app.services.progressive_difficulty_engine import ProgressiveDifficultyEngine
from app.services.spaced_repetition_scheduler import SpacedRepetitionScheduler
from fastapi import Request

# Configure more detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set logging levels
logging.getLogger('httpx').setLevel(logging.WARNING)  # Reduce noise from HTTP requests
logging.getLogger('app').setLevel(logging.DEBUG)     # More details for app logs

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routes import agents, quizzes

app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["quizzes"])

@app.get("/")
async def root():
    return {"message": "Cybersecurity Quiz AI Backend"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/skill-improvement")
async def generate_skill_improvement(request: Request):
    """Generate skill improvement activities"""
    data = await request.json()
    result = agent_executor.execute_agent("SkillImprovementAgent", data)
    return result
@app.post("/api/spaced-repetition/schedule")
async def schedule_repetition(request: Request):
    """Schedule a spaced repetition session"""
    data = await request.json()
    scheduler = SpacedRepetitionScheduler()
    result = scheduler.schedule_repetition(
        data.get('user_id'),
        data.get('skill_id'),
        data.get('difficulty', 3),
        data.get('performance_rating')
    )
    return {"status": "success", "schedule": result}

@app.post("/api/spaced-repetition/complete")
async def complete_repetition(request: Request):
    """Complete a spaced repetition session"""
    data = await request.json()
    scheduler = SpacedRepetitionScheduler()
    result = scheduler.complete_repetition(
        data.get('schedule_id'),
        data.get('performance_rating')
    )
    return {"status": "success", "next_schedule": result}
def setup_agents():
    # Register existing agents
    # ...
    
    # Register new agent
    agent_executor.register_agent(SkillImprovementAgent())
    
    return agent_executor