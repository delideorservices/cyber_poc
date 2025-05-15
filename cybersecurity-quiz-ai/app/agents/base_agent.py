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
        Validate that the inputs dictionary contains all required keys with valid values
        
        Args:
            inputs: Dictionary of inputs to validate
            required_keys: List of required keys
            
        Raises:
            ValueError: If any required key is missing or has an invalid value
        """
        print(f"Validating inputs: {list(inputs.keys())}")
        print(f"Required keys: {required_keys}")
        
        for key in required_keys:
            if key not in inputs:
                print(f"Missing required input: {key}")
                raise ValueError(f"Missing required input: {key}")
            
            # Check if the value is None or empty string
            value = inputs.get(key)
            print(f"Checking key '{key}' with value: {value}")
            
            if value is None:
                print(f"Required input '{key}' is None")
                raise ValueError(f"Required input '{key}' is None")
                
            if isinstance(value, str) and value.strip() == '':
                print(f"Required input '{key}' is empty string")
                raise ValueError(f"Required input '{key}' is empty string")
        
        print("All required inputs validated successfully")
