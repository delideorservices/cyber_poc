import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database Configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "cybersecurity_quiz")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

# Database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
LEARNING_PLAN_CONFIG = {
    # Maximum duration for a learning plan in weeks
    'max_plan_duration_weeks': 26,
    
    # Minimum duration for a learning plan in weeks
    'min_plan_duration_weeks': 4,
    
    # Maximum modules per plan
    'max_modules_per_plan': 8,
    
    # Default resources to include when no specific resources are found
    'default_resources': [
        {
            'id': None,
            'title': 'OWASP Top 10',
            'type': 'website',
            'url': 'https://owasp.org/www-project-top-ten/',
            'difficulty': 'intermediate'
        },
        {
            'id': None,
            'title': 'NIST Cybersecurity Framework',
            'type': 'guide',
            'url': 'https://www.nist.gov/cyberframework',
            'difficulty': 'intermediate'
        }
    ],
    
    # Learning plan difficulty calculation settings
    'difficulty_mapping': {
        'beginner': {
            'duration_multiplier': 1.5,
            'module_count': 4,
            'resources_per_module': 3
        },
        'intermediate': {
            'duration_multiplier': 1.0,
            'module_count': 6,
            'resources_per_module': 4
        },
        'advanced': {
            'duration_multiplier': 0.75,
            'module_count': 8,
            'resources_per_module': 5
        }
    }
}