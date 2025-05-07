from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.db_service import db_service
import json
class TopicMapperAgent(BaseAgent):
    """Agent for mapping user input topics to database categories"""
    
    def __init__(self):
        super().__init__(
            name="TopicMapperAgent",
            description="Maps user input topics to database categories"
        )
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a topic to related categories
        
        Args:
            inputs: Dictionary containing topic_id and user profile analysis
            
        Returns:
            Dictionary with mapped topic data
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['topic_id', 'user_id'])
        
        topic_id = inputs['topic_id']
        
        # Get topic data
        topic = db_service.fetch_one(
            "SELECT * FROM topics WHERE id = %s",
            (topic_id,)
        )
        
        if not topic:
            raise ValueError(f"Topic with ID {topic_id} not found")
        
        # Get related topics based on keywords
        related_topics = []
        if topic.get('keywords'):
            keyword_params = []
            query_parts = []
            
            for keyword in topic.get('keywords', []):
             if keyword and keyword.strip():
                query_parts.append("keywords::jsonb @> %s::jsonb")
                keyword_params.append(json.dumps([keyword]))
            
            if query_parts:
                related_query = f"""
                SELECT * FROM topics 
                WHERE id != %s AND ({' OR '.join(query_parts)})
                LIMIT 3
                """
                
                param_list = [topic_id] + keyword_params
                related_topics = db_service.fetch_all(related_query, tuple(param_list))
        
        # Map to relevant sector if applicable
        sector_id = topic.get('sector_id')
        sector = None
        
        if sector_id:
            sector = db_service.fetch_one(
                "SELECT * FROM sectors WHERE id = %s",
                (sector_id,)
            )
        
        # Create mapping result
        mapping_result = {
            'user_id': inputs['user_id'],
            'topic_id': topic_id,
            'topic_name': topic.get('name'),
            'topic_description': topic.get('description'),
            'topic_keywords': topic.get('keywords', []),
            'sector_specific': True if sector_id else False,
            'sector': sector.get('name') if sector else None,
            'related_topics': [rt.get('name') for rt in related_topics],
            'experience_level': inputs.get('experience_level', 1),
            'focus_areas': inputs.get('focus_areas', []),
            'user_role': inputs.get('role'),
            'user_sector': inputs.get('sector'),
            'status': 'success',
            'next_agent': 'quiz_generator'
        }
        
        return mapping_result