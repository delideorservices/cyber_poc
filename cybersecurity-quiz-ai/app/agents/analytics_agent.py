from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.db_service import db_service

class AnalyticsAgent(BaseAgent):
    """Agent for analyzing user performance across quizzes"""
    
    def __init__(self):
        super().__init__(
            name="AnalyticsAgent",
            description="Analyzes user performance across quizzes to provide insights"
        )
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user performance across quizzes
        
        Args:
            inputs: Dictionary containing user_id and current quiz result
            
        Returns:
            Dictionary with analytics insights
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['user_id'])
        
        user_id = inputs['user_id']
        
        # Get user info
        user = db_service.fetch_one(
            """
            SELECT u.*, s.name as sector_name, r.name as role_name
            FROM users u
            LEFT JOIN sectors s ON u.sector_id = s.id
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
            """,
            (user_id,)
        )
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get all user quiz results
        results = db_service.fetch_all(
            """
            SELECT uqr.*, q.title as quiz_title, q.topic_id, t.name as topic_name
            FROM user_quiz_results uqr
            JOIN quizzes q ON uqr.quiz_id = q.id
            JOIN topics t ON q.topic_id = t.id
            WHERE uqr.user_id = %s
            ORDER BY uqr.completed_at DESC
            """,
            (user_id,)
        )
        
        # Calculate performance metrics
        performance_summary = self._calculate_performance_summary(results)
        
        # Identify strongest and weakest areas
        strengths, weaknesses = self._identify_strengths_weaknesses(results)
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(
            weaknesses, user['sector_name'], user['role_name']
        )
        
        # Recommend next quizzes
        next_quiz_recommendations = self._recommend_next_quizzes(
            results, weaknesses, user['sector_id']
        )
        
        # Compile analytics
        analytics = {
            'user_id': user_id,
            'performance_summary': performance_summary,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'improvement_suggestions': improvement_suggestions,
            'next_quiz_recommendations': next_quiz_recommendations,
            'status': 'success',
            'next_agent': 'learning_plan_agent'
        }
        
        return analytics
    
    def _calculate_performance_summary(self, results: List[Dict]) -> Dict:
        """
        Calculate overall performance summary across all quizzes
        
        Args:
            results: List of quiz results
            
        Returns:
            Dictionary with performance metrics
        """
        if not results:
            return {
                'total_quizzes': 0,
                'average_score': 0,
                'trend': 'no_data'
            }
        
        total_quizzes = len(results)
        average_score = sum(r['percentage_score'] for r in results) / total_quizzes
        
        # Calculate trend (improving, steady, declining)
        if total_quizzes >= 3:
            recent_three = results[:3]  # Most recent 3 quizzes
            recent_avg = sum(r['percentage_score'] for r in recent_three) / 3
            
            older = results[3:] if len(results) > 3 else []
            older_avg = sum(r['percentage_score'] for r in older) / len(older) if older else recent_avg
            
            diff = recent_avg - older_avg
            if diff > 5:
                trend = 'improving'
            elif diff < -5:
                trend = 'declining'
            else:
                trend = 'steady'
        else:
            trend = 'insufficient_data'
        
        return {
            'total_quizzes': total_quizzes,
            'average_score': round(average_score, 2),
            'trend': trend
        }
    
    def _identify_strengths_weaknesses(self, results: List[Dict]) -> tuple:
        """
        Identify strongest and weakest areas based on chapter scores
        
        Args:
            results: List of quiz results
            
        Returns:
            Tuple of (strengths, weaknesses) lists
        """
        # Aggregate chapter scores across all quizzes
        chapter_scores = {}
        
        for result in results:
            if not result.get('chapter_scores'):
                continue
                
            try:
                chapters = result['chapter_scores']
                if isinstance(chapters, str):
                    chapters = json.loads(chapters)
                    
                for chapter, score in chapters.items():
                    if chapter not in chapter_scores:
                        chapter_scores[chapter] = []
                    
                    # Add percentage score
                    chapter_scores[chapter].append(
                        score['percentage'] if isinstance(score, dict) else float(score)
                    )
            except:
                continue
        
        # Calculate average scores for each chapter
        avg_scores = {}
        for chapter, scores in chapter_scores.items():
            if scores:
                avg_scores[chapter] = sum(scores) / len(scores)
        
        # Identify strengths (top 3)
        strengths = sorted(
            [(chapter, score) for chapter, score in avg_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Identify weaknesses (bottom 3)
        weaknesses = sorted(
            [(chapter, score) for chapter, score in avg_scores.items()],
            key=lambda x: x[1]
        )[:3]
        
        return (
            [{'area': s[0], 'score': round(s[1], 2)} for s in strengths],
            [{'area': w[0], 'score': round(w[1], 2)} for w in weaknesses]
        )
    def _generate_improvement_suggestions(self, weaknesses: List[Dict], sector: str, role: str) -> List[str]:
            """
            Generate improvement suggestions based on weak areas
            
            Args:
                weaknesses: List of weak areas
                sector: User's sector
                role: User's role
                
            Returns:
                List of improvement suggestions
            """
            suggestions = []
            
            for weakness in weaknesses:
                area = weakness['area']
                score = weakness['score']
                
                # Generate specific suggestions based on weak area
                if 'Basics' in area:
                    suggestions.append("Review fundamental cybersecurity concepts through online tutorials.")
                    suggestions.append("Practice identifying common security threats in your daily work.")
                    
                elif 'Risks' in area and role:
                    suggestions.append(f"Focus on security procedures specific to your {role} role.")
                    suggestions.append("Consult with colleagues about best security practices in your position.")
                    
                elif 'Threats' in area and sector:
                    suggestions.append(f"Study recent security incidents in the {sector} sector.")
                    suggestions.append(f"Review {sector}-specific compliance requirements and standards.")
                    
                elif 'Advanced' in area:
                    suggestions.append("Consider formal cybersecurity training to build advanced knowledge.")
                    suggestions.append("Explore hands-on security labs to practice advanced skills.")
                    
                else:
                    suggestions.append(f"Allocate more study time to {area}.")
                    suggestions.append(f"Seek additional resources about {area}.")
            
            # Add general suggestion if list is empty
            if not suggestions:
                suggestions.append("Continue practicing regular cybersecurity awareness exercises.")
                suggestions.append("Consider exploring more advanced cybersecurity topics to expand your knowledge.")
            
            return suggestions[:5]  # Return up to 5 suggestions
    def _recommend_next_quizzes(self, results: List[Dict], weaknesses: List[Dict], sector_id: int) -> List[Dict]:
            """
            Recommend next quizzes based on performance and weak areas
            
            Args:
                results: List of quiz results
                weaknesses: List of weak areas
                sector_id: User's sector ID
                
            Returns:
                List of recommended quiz topics
            """
            # Get completed quiz topics
            completed_topic_ids = [r['topic_id'] for r in results]
            
            # Find topics related to weak areas
            recommended_topics = []
            
            for weakness in weaknesses:
                area = weakness['area']
                
                # Query topics based on weakness
                query_params = []
                
                # Handle the case when no topics are completed yet
                if not completed_topic_ids:
                    query = """
                    SELECT id, name, description FROM topics 
                    WHERE (
                    """
                else:
                    # Original code for when completed_topic_ids is not empty
                    query = """
                    SELECT id, name, description FROM topics 
                    WHERE id NOT IN (
                    """
                    
                    # Add completed topic IDs to exclusion list
                    for i, topic_id in enumerate(completed_topic_ids):
                        query += "%s"
                        if i < len(completed_topic_ids) - 1:
                            query += ", "
                        query_params.append(topic_id)
                    
                    query += ") AND ("
                
                # Add search terms based on weakness area
                search_terms = []
                if 'Basics' in area:
                    search_terms.append("name ILIKE '%basic%' OR description ILIKE '%basic%'")
                elif 'Risks' in area:
                    search_terms.append("name ILIKE '%risk%' OR description ILIKE '%risk%'")
                elif 'Threats' in area:
                    search_terms.append("name ILIKE '%threat%' OR description ILIKE '%threat%'")
                elif 'Advanced' in area:
                    search_terms.append("name ILIKE '%advanced%' OR description ILIKE '%advanced%'")
                else:
                    # Use weakness area words as search terms
                    words = area.split()
                    for word in words:
                        if len(word) > 3:  # Only use meaningful words
                            search_terms.append(f"name ILIKE '%{word}%' OR description ILIKE '%{word}%'")
                
                if not search_terms:
                    continue
                    
                query += " OR ".join(search_terms)
                query += ")"
                
                # Prefer sector-specific topics if applicable
                if sector_id:
                    query += " ORDER BY CASE WHEN sector_id = %s THEN 0 ELSE 1 END"
                    query_params.append(sector_id)
                
                query += " LIMIT 2"  # Get top 2 topics per weakness
                
                topics = db_service.fetch_all(query, tuple(query_params))
                
                for topic in topics:
                    if topic not in recommended_topics:
                        recommended_topics.append({
                            'id': topic['id'],
                            'name': topic['name'],
                            'description': topic['description']
                        })
            
            # If no specific recommendations, get general topics
            if not recommended_topics:
                if completed_topic_ids:
                    general_query = """
                    SELECT id, name, description FROM topics 
                    WHERE id NOT IN ({}) 
                    ORDER BY RANDOM() LIMIT 3
                    """.format(','.join(['%s'] * len(completed_topic_ids)))
                    general_topics = db_service.fetch_all(general_query, tuple(completed_topic_ids))
                else:
                    # No completed topics, get any random topics
                    general_query = """
                    SELECT id, name, description FROM topics 
                    ORDER BY RANDOM() LIMIT 3
                    """
                    general_topics = db_service.fetch_all(general_query)
                
                recommended_topics = [
                    {'id': t['id'], 'name': t['name'], 'description': t['description']}
                    for t in general_topics
                ]
            
            return recommended_topics[:3]
