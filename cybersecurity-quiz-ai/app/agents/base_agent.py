import os
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import openai
from langchain.llms import OpenAI
from crewai import Agent, Task, Crew
from dotenv import load_dotenv

# Import utility functions
from utils.db_connector import DatabaseConnector

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base agent class that provides common functionality for all agents.
    All specific agents should inherit from this class.
    """
    
    def __init__(self):
        """
        Initialize the base agent with common configurations.
        """
        # Set up OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize database connector
        self.db = DatabaseConnector()
        
        # Set up LangChain LLM
        self.llm = OpenAI(
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Set up agent name
        self.agent_name = self.__class__.__name__
        
        logger.info(f"Initialized {self.agent_name}")
    
    def build_crew_agent(self, name: str, role: str, goal: str):
        """
        Create a CrewAI agent with the given parameters.
        
        Args:
            name: The name of the agent
            role: The role of the agent
            goal: The goal of the agent
        
        Returns:
            Agent: A CrewAI agent
        """
        return Agent(
            name=name,
            role=role,
            goal=goal,
            backstory=f"You are an AI assistant specialized in {role.lower()}.",
            verbose=True,
            llm=self.llm
        )
    
    def create_task(self, agent, description: str, expected_output: str):
        """
        Create a task for a CrewAI agent.
        
        Args:
            agent: The CrewAI agent
            description: The task description
            expected_output: The expected output format
        
        Returns:
            Task: A CrewAI task
        """
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent
        )
    
    def execute_crew(self, agents: List, tasks: List):
        """
        Execute a crew of agents with the given tasks.
        
        Args:
            agents: List of CrewAI agents
            tasks: List of CrewAI tasks
        
        Returns:
            Any: The result of the crew execution
        """
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=2
        )
        return crew.kickoff()
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get user data from the database.
        
        Args:
            user_id: The user ID
        
        Returns:
            Dict: User data
        """
        return self.db.get_user_data(user_id)
    
    def get_user_skills(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get user skills from the database.
        
        Args:
            user_id: The user ID
        
        Returns:
            List[Dict]: User skills
        """
        return self.db.get_user_skills(user_id)
    
    def get_user_quiz_results(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get user quiz results from the database.
        
        Args:
            user_id: The user ID
            limit: Optional limit on the number of results
        
        Returns:
            List[Dict]: User quiz results
        """
        return self.db.get_user_quiz_results(user_id, limit)
    
    def save_to_database(self, table: str, data: Dict[str, Any]) -> int:
        """
        Save data to the database.
        
        Args:
            table: The database table
            data: The data to save
        
        Returns:
            int: The ID of the inserted record
        """
        return self.db.insert(table, data)
    
    def update_in_database(self, table: str, record_id: int, data: Dict[str, Any]) -> bool:
        """
        Update data in the database.
        
        Args:
            table: The database table
            record_id: The ID of the record to update
            data: The data to update
        
        Returns:
            bool: Whether the update was successful
        """
        return self.db.update(table, record_id, data)
    
    @abstractmethod
    def execute(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        This method must be implemented by all subclasses.
        
        Args:
            user_id: The user ID
            data: Additional data for the agent
        
        Returns:
            Dict: The result of the agent execution
        """
        pass