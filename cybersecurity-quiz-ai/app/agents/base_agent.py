from langchain.agents import AgentExecutor
from langchain.schema import HumanMessage
from app.services.db_service import db_service
from typing import Dict, Any, List, Optional

class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent's main functionality
        
        Args:
            inputs: Dictionary of input parameters
            
        Returns:
            Dictionary containing results
        """
        try:
            # Log the start of agent execution
            db_service.log_agent_action(
                agent_name=self.name,
                action="execute",
                input_data=inputs,
                status="running"
            )
            
            # Execute agent logic - to be implemented by subclasses
            result = self._execute(inputs)
            
            # Log successful completion
            db_service.log_agent_action(
                agent_name=self.name,
                action="execute",
                input_data=inputs,
                output_data=result,
                status="success"
            )
            
            return result
            
        except Exception as e:
            # Log error
            db_service.log_agent_action(
                agent_name=self.name,
                action="execute",
                input_data=inputs,
                status="error",
                error_message=str(e)
            )
            
            # Re-raise the exception
            raise
        
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution logic - to be implemented by subclasses
        
        Args:
            inputs: Dictionary of input parameters
            
        Returns:
            Dictionary containing results
        """
        raise NotImplementedError("Subclasses must implement _execute method")
        
    def _validate_inputs(self, inputs: Dict[str, Any], required_keys: List[str]) -> None:
        """
        Validate that required keys are present in inputs
        
        Args:
            inputs: Dictionary of input parameters
            required_keys: List of required keys
            
        Raises:
            ValueError: If a required key is missing
        """
        for key in required_keys:
            if key not in inputs:
                raise ValueError(f"Missing required input: {key}")