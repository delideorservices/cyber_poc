import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

