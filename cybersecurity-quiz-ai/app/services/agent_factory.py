from app.agents.registration_agent import RegistrationAgent
from app.agents.profile_analyzer_agent import ProfileAnalyzerAgent
from app.agents.topic_mapper_agent import TopicMapperAgent
from app.agents.quiz_generator_agent import QuizGeneratorAgent
from app.agents.quiz_formatter_agent import QuizFormatterAgent
from app.agents.quiz_delivery_agent import QuizDeliveryAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.feedback_agent import FeedbackAgent
from app.agents.recommendation_agent import RecommendationAgent

def get_agent(agent_name):
    """Factory method to get an agent instance by name"""
    agents = {
        'registration': RegistrationAgent,
        'profile_analyzer': ProfileAnalyzerAgent,
        'topic_mapper': TopicMapperAgent,
        'quiz_generator': QuizGeneratorAgent,
        'quiz_formatter': QuizFormatterAgent,
        'quiz_delivery': QuizDeliveryAgent,
        'evaluation': EvaluationAgent,
        'analytics': AnalyticsAgent,
        'feedback': FeedbackAgent,
        # New agent
        'recommendation': RecommendationAgent,
    }

    if agent_name.lower() not in agents:
        raise ValueError(f"Unknown agent: {agent_name}")

    return agents[agent_name.lower()]()