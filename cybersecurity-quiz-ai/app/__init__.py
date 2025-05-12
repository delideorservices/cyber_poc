from app.agents.registration_agent import RegistrationAgent
from app.agents.profile_analyzer_agent import ProfileAnalyzerAgent
from app.agents.topic_mapper_agent import TopicMapperAgent
from app.agents.quiz_generator_agent import QuizGeneratorAgent
from app.agents.quiz_formatter_agent import QuizFormatterAgent
from app.agents.quiz_delivery_agent import QuizDeliveryAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.feedback_agent import FeedbackAgent
# Import the new Learning Plan Agent
from app.agents.learning_plan_agent import LearningPlanAgent

# Register agents in the application
def register_agents():
    """Register all agents with the application"""
    agents = {
        'registration_agent': RegistrationAgent,
        'profile_analyzer_agent': ProfileAnalyzerAgent,
        'topic_mapper_agent': TopicMapperAgent,
        'quiz_generator_agent': QuizGeneratorAgent,
        'quiz_formatter_agent': QuizFormatterAgent,
        'quiz_delivery_agent': QuizDeliveryAgent,
        'evaluation_agent': EvaluationAgent,
        'analytics_agent': AnalyticsAgent,
        'learning_plan_agent': LearningPlanAgent,  # Add the new agent
        'feedback_agent': FeedbackAgent
    }
    
    return agents