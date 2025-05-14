from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.agents.learning_plan_agent import LearningPlanAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.skill_improvement_agent import SkillImprovementAgent
from app.agents.recommendation_agent import RecommendationAgent

app = FastAPI(title="CYX3.0 Agent Service API")

class AgentRequest(BaseModel):
    user_id: int
    data: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "CYX3.0 Agent Service API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/agent/learning_plan_agent")
async def execute_learning_plan_agent(request: AgentRequest):
    try:
        agent = LearningPlanAgent()
        result = agent.execute(request.user_id, request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/analytics_agent")
async def execute_analytics_agent(request: AgentRequest):
    try:
        agent = AnalyticsAgent()
        result = agent.execute(request.user_id, request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/skill_improvement_agent")
async def execute_skill_improvement_agent(request: AgentRequest):
    try:
        agent = SkillImprovementAgent()
        result = agent.execute(request.user_id, request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/recommendation_agent")
async def execute_recommendation_agent(request: AgentRequest):
    try:
        agent = RecommendationAgent()
        result = agent.execute(request.user_id, request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/test/{agent_name}")
async def test_agent(agent_name: str):
    """Test endpoint to verify agent availability"""
    valid_agents = ["learning_plan_agent", "analytics_agent", 
                  "skill_improvement_agent", "recommendation_agent"]
    
    if agent_name not in valid_agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        
    return {"status": "success", "message": f"Agent {agent_name} is available"}