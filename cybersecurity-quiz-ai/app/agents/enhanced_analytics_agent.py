from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
import logging
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

class EnhancedAnalyticsAgent(BaseAgent):
    """Agent for analyzing user quiz performance with enhanced metrics and visualizations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "EnhancedAnalyticsAgent"
        self.description = "Analyzes user performance with detailed strength/weakness identification"
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user quiz results and generate enhanced analytics
        
        Args:
            inputs: Dictionary containing user_id and quiz_id
            
        Returns:
            Dictionary with analysis results including strengths, weaknesses, and visualizations
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['user_id', 'quiz_id'])
        
        user_id = inputs['user_id']
        quiz_id = inputs['quiz_id']
        
        # Get quiz results
        quiz_results = self._get_quiz_results(user_id, quiz_id)
        
        # Get all user responses for this quiz
        responses = self._get_user_responses(user_id, quiz_id)
        
        # Get question data for context
        questions = self._get_questions(quiz_id)
        
        # Get topic and skill data
        topic_id = quiz_results['topic_id']
        topic = self._get_topic_data(topic_id)
        skills = self._get_relevant_skills(topic_id)
        
        # Calculate strength/weakness metrics
        strength_weakness = self._analyze_strength_weakness(responses, questions, skills)
        
        # Calculate skill proficiency scores
        skill_proficiency = self._calculate_skill_proficiency(responses, questions, skills)
        
        # Compare with similar users (peer comparison)
        peer_comparison = self._generate_peer_comparison(user_id, topic_id, skill_proficiency)
        
        # Generate improvement recommendations
        recommendations = self._generate_recommendations(strength_weakness, skill_proficiency)
        
        # Generate visualization data
        visualization_data = self._prepare_visualization_data(
            skill_proficiency, 
            peer_comparison,
            strength_weakness
        )
        
        # Prepare complete analysis results
        analysis_results = {
            'user_id': user_id,
            'quiz_id': quiz_id, 
            'topic_id': topic_id,
            'topic_name': topic['name'],
            'overall_score': quiz_results['percentage_score'],
            'strength_weakness': strength_weakness,
            'skill_proficiency': skill_proficiency,
            'peer_comparison': peer_comparison,
            'recommendations': recommendations,
            'visualization_data': visualization_data,
            'status': 'success'
        }
        
        return analysis_results
    
    def _get_quiz_results(self, user_id, quiz_id):
        """Fetch overall quiz results from database"""
        query = """
            SELECT * FROM user_quiz_results 
            WHERE user_id = %s AND quiz_id = %s
        """
        return self.db_service.fetch_one(query, (user_id, quiz_id))
    
    def _get_user_responses(self, user_id, quiz_id):
        """Fetch all user responses for a specific quiz"""
        query = """
            SELECT ur.* 
            FROM user_responses ur
            JOIN questions q ON ur.question_id = q.id
            JOIN chapters c ON q.chapter_id = c.id
            WHERE ur.user_id = %s AND c.quiz_id = %s
        """
        return self.db_service.fetch_all(query, (user_id, quiz_id))
    
    def _get_questions(self, quiz_id):
        """Fetch all questions for a specific quiz with metadata"""
        query = """
            SELECT q.*, c.title as chapter_title, c.sequence as chapter_sequence
            FROM questions q
            JOIN chapters c ON q.chapter_id = c.id
            WHERE c.quiz_id = %s
            ORDER BY c.sequence, q.sequence
        """
        return self.db_service.fetch_all(query, (quiz_id,))
    
    def _get_topic_data(self, topic_id):
        """Fetch topic data"""
        query = "SELECT * FROM topics WHERE id = %s"
        return self.db_service.fetch_one(query, (topic_id,))
    
    def _get_relevant_skills(self, topic_id):
        """Get skills relevant to the topic"""
        # This query assumes we've created the topic_skills table in Phase 1
        query = """
            SELECT s.* 
            FROM skills s
            JOIN topic_skills ts ON s.id = ts.skill_id
            WHERE ts.topic_id = %s
        """
        return self.db_service.fetch_all(query, (topic_id,))
    
    def _analyze_strength_weakness(self, responses, questions, skills):
        """
        Analyze user responses to identify strengths and weaknesses
        Uses more sophisticated algorithms than the basic analytics
        """
        # Group questions by skill
        skill_questions = {}
        for question in questions:
            skill_id = question.get('skill_id')
            if skill_id not in skill_questions:
                skill_questions[skill_id] = []
            skill_questions[skill_id].append(question)
        
        # Calculate performance by skill
        skill_performance = {}
        for skill in skills:
            skill_id = skill['id']
            if skill_id not in skill_questions or not skill_questions[skill_id]:
                continue
                
            # Get questions for this skill
            skill_q_ids = [q['id'] for q in skill_questions[skill_id]]
            
            # Filter responses for these questions
            skill_responses = [r for r in responses if r['question_id'] in skill_q_ids]
            
            if not skill_responses:
                continue
                
            # Calculate metrics
            correct = sum(1 for r in skill_responses if r['is_correct'])
            total = len(skill_responses)
            score = (correct / total) * 100 if total > 0 else 0
            
            # Calculate time efficiency (if 'answered_at' timestamps are available)
            avg_time = 0
            if all('answered_at' in r for r in skill_responses):
                times = [r['answered_at'] - r['created_at'] for r in skill_responses]
                avg_time = sum(times) / len(times) if times else 0
            
            # Calculate confidence score (optional - if we track attempts)
            # This is a simple implementation - could be enhanced
            confidence = 100  # Default high confidence
            
            skill_performance[skill_id] = {
                'skill_id': skill_id,
                'skill_name': skill['name'],
                'score': score,
                'correct': correct,
                'total': total,
                'avg_time': avg_time,
                'confidence': confidence
            }
        
        # Determine strengths and weaknesses based on score thresholds
        strengths = []
        weaknesses = []
        needs_improvement = []
        
        for skill_id, perf in skill_performance.items():
            # Find corresponding skill object
            skill = next((s for s in skills if s['id'] == skill_id), None)
            if not skill:
                continue
                
            if perf['score'] >= 80:
                strengths.append({
                    'skill_id': skill_id,
                    'skill_name': skill['name'],
                    'score': perf['score'],
                    'confidence': perf['confidence']
                })
            elif perf['score'] <= 50:
                weaknesses.append({
                    'skill_id': skill_id,
                    'skill_name': skill['name'],
                    'score': perf['score'],
                    'confidence': perf['confidence']
                })
            else:
                needs_improvement.append({
                    'skill_id': skill_id,
                    'skill_name': skill['name'],
                    'score': perf['score'],
                    'confidence': perf['confidence']
                })
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'needs_improvement': needs_improvement,
            'skill_performance': skill_performance
        }
    
    def _calculate_skill_proficiency(self, responses, questions, skills):
        """
        Calculate detailed skill proficiency scores using advanced metrics
        """
        # Map questions to skills
        question_skill_map = {q['id']: q.get('skill_id') for q in questions}
        
        # Calculate base scores
        skill_scores = {}
        for skill in skills:
            skill_id = skill['id']
            skill_scores[skill_id] = {
                'skill_id': skill_id,
                'skill_name': skill['name'],
                'responses': []
            }
        
        # Collect response data for each skill
        for response in responses:
            question_id = response['question_id']
            if question_id in question_skill_map:
                skill_id = question_skill_map[question_id]
                if skill_id in skill_scores:
                    skill_scores[skill_id]['responses'].append(response)
        
        # Calculate proficiency metrics for each skill
        proficiency_scores = {}
        for skill_id, data in skill_scores.items():
            if not data['responses']:
                continue
                
            # Calculate basic metrics
            total = len(data['responses'])
            correct = sum(1 for r in data['responses'] if r['is_correct'])
            points = sum(r['points_earned'] for r in data['responses'])
            
            # Calculate score percentage
            score_pct = (correct / total) * 100 if total > 0 else 0
            
            # Calculate mastery level (1-5 scale)
            mastery_level = 1
            if score_pct >= 95:
                mastery_level = 5
            elif score_pct >= 85:
                mastery_level = 4
            elif score_pct >= 70:
                mastery_level = 3
            elif score_pct >= 50:
                mastery_level = 2
            
            # Calculate confidence interval (more statistically sound)
            if total >= 5:  # Need minimum sample size
                mean = score_pct / 100
                # Wilson score interval
                confidence = 0.95  # 95% confidence
                z = stats.norm.ppf(1 - (1 - confidence) / 2)
                
                # Wilson score interval formula
                denominator = 1 + z**2/total
                centre_adjusted_probability = mean + z**2/(2*total)
                adjusted_standard_deviation = sqrt((mean*(1-mean) + z**2/(4*total))/total)
                
                lower_bound = (centre_adjusted_probability - z*adjusted_standard_deviation) / denominator
                upper_bound = (centre_adjusted_probability + z*adjusted_standard_deviation) / denominator
                
                confidence_interval = (lower_bound * 100, upper_bound * 100)
            else:
                confidence_interval = (max(0, score_pct - 20), min(100, score_pct + 20))
            
            proficiency_scores[skill_id] = {
                'skill_id': skill_id,
                'skill_name': data['skill_name'],
                'score_percentage': score_pct,
                'correct_answers': correct,
                'total_questions': total,
                'points_earned': points,
                'mastery_level': mastery_level,
                'confidence_interval': confidence_interval
            }
        
        return proficiency_scores
    
    def _generate_peer_comparison(self, user_id, topic_id, skill_proficiency):
        """
        Compare user's performance with peers (similar role, sector, experience)
        """
        # Get user data for context
        user = self.db_service.fetch_one(
            "SELECT sector_id, role_id, years_experience FROM users WHERE id = %s",
            (user_id,)
        )
        
        if not user:
            return {}
            
        sector_id = user['sector_id']
        role_id = user['role_id']
        years_exp = user['years_experience']
        
        # Find similar users
        similar_users_query = """
            SELECT id FROM users 
            WHERE sector_id = %s 
            AND role_id = %s
            AND years_experience BETWEEN %s AND %s
            AND id != %s
            LIMIT 100
        """
        exp_min = max(0, years_exp - 2)
        exp_max = years_exp + 2
        similar_users = self.db_service.fetch_all(
            similar_users_query, 
            (sector_id, role_id, exp_min, exp_max, user_id)
        )
        
        similar_user_ids = [u['id'] for u in similar_users]
        
        # If no similar users found, use a broader criteria
        if not similar_user_ids:
            similar_users = self.db_service.fetch_all(
                "SELECT id FROM users WHERE sector_id = %s AND id != %s LIMIT 100",
                (sector_id, user_id)
            )
            similar_user_ids = [u['id'] for u in similar_users]
        
        if not similar_user_ids:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough peer data available for comparison'
            }
        
        # Get average scores for these users by skill for this topic
        peer_scores_query = """
            SELECT 
                q.skill_id,
                AVG(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) * 100 as avg_score,
                COUNT(DISTINCT uqr.user_id) as user_count
            FROM user_quiz_results uqr
            JOIN user_responses ur ON uqr.user_id = ur.user_id
            JOIN questions q ON ur.question_id = q.id
            WHERE uqr.user_id IN %s
            AND uqr.topic_id = %s
            AND q.skill_id IS NOT NULL
            GROUP BY q.skill_id
        """
        peer_scores = self.db_service.fetch_all(
            peer_scores_query,
            (tuple(similar_user_ids), topic_id)
        )
        
        # Format comparison data
        skill_comparison = {}
        for skill_id, prof in skill_proficiency.items():
            # Find peer average for this skill
            peer_avg = next(
                (p['avg_score'] for p in peer_scores if p['skill_id'] == skill_id), 
                None
            )
            
            if peer_avg is not None:
                user_score = prof['score_percentage']
                percentile = self._calculate_percentile(user_score, peer_avg)
                
                skill_comparison[skill_id] = {
                    'skill_id': skill_id,
                    'skill_name': prof['skill_name'],
                    'user_score': user_score,
                    'peer_average': peer_avg,
                    'percentile': percentile,
                    'differential': user_score - peer_avg
                }
        
        return {
            'skill_comparison': skill_comparison,
            'peer_count': len(similar_user_ids),
            'status': 'success'
        }
    
    def _calculate_percentile(self, user_score, peer_avg, std_dev=15):
        """
        Calculate approximate percentile of user score compared to peer distribution
        Assuming a normal distribution with the given standard deviation
        """
        z_score = (user_score - peer_avg) / std_dev
        percentile = stats.norm.cdf(z_score) * 100
        return round(percentile, 1)
    
    def _generate_recommendations(self, strength_weakness, skill_proficiency):
        """
        Generate personalized recommendations based on identified weaknesses
        """
        recommendations = []
        
        # Focus on top 3 weaknesses
        for weakness in strength_weakness['weaknesses'][:3]:
            skill_id = weakness['skill_id']
            skill_name = weakness['skill_name']
            
            # Get learning resources for this skill
            resources_query = """
                SELECT * FROM learning_resources 
                WHERE skill_id = %s 
                ORDER BY effectiveness_rating DESC
                LIMIT 3
            """
            resources = self.db_service.fetch_all(resources_query, (skill_id,))
            
            # Create recommendation
            recommendation = {
                'skill_id': skill_id,
                'skill_name': skill_name,
                'score': weakness['score'],
                'message': f"Focus on improving your {skill_name} skills",
                'resources': resources,
                'practice_quiz_ids': self._get_practice_quizzes(skill_id)
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _get_practice_quizzes(self, skill_id):
        """Find suitable practice quizzes for a specific skill"""
        query = """
            SELECT DISTINCT q.id 
            FROM quizzes q
            JOIN chapters c ON c.quiz_id = q.id
            JOIN questions qn ON qn.chapter_id = c.id
            WHERE qn.skill_id = %s
            AND q.difficulty_level <= 3
            LIMIT 3
        """
        quizzes = self.db_service.fetch_all(query, (skill_id,))
        return [q['id'] for q in quizzes]
    
    def _prepare_visualization_data(self, skill_proficiency, peer_comparison, strength_weakness):
        """
        Prepare data structures for frontend visualizations
        """
        # Radar chart data (skill proficiency)
        radar_data = {
            'labels': [],
            'datasets': [
                {
                    'label': 'Your Score',
                    'data': [],
                    'fill': True,
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgb(54, 162, 235)',
                    'pointRadius': 5
                }
            ]
        }
        
        if 'skill_comparison' in peer_comparison:
            radar_data['datasets'].append({
                'label': 'Peer Average',
                'data': [],
                'fill': True,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgb(255, 99, 132)',
                'pointRadius': 5
            })
        
        # Prepare radar chart data
        for skill_id, prof in skill_proficiency.items():
            radar_data['labels'].append(prof['skill_name'])
            radar_data['datasets'][0]['data'].append(prof['score_percentage'])
            
            # Add peer data if available
            if 'skill_comparison' in peer_comparison and skill_id in peer_comparison['skill_comparison']:
                radar_data['datasets'][1]['data'].append(
                    peer_comparison['skill_comparison'][skill_id]['peer_average']
                )
            elif len(radar_data['datasets']) > 1:
                radar_data['datasets'][1]['data'].append(0)
        
        # Bar chart for strengths and weaknesses
        bar_chart_data = {
            'strengths': {
                'labels': [s['skill_name'] for s in strength_weakness['strengths']],
                'data': [s['score'] for s in strength_weakness['strengths']]
            },
            'weaknesses': {
                'labels': [w['skill_name'] for w in strength_weakness['weaknesses']],
                'data': [w['score'] for w in strength_weakness['weaknesses']]
            }
        }
        
        # Heat map data (for detailed skill analysis)
        heatmap_data = []
        for skill_id, prof in skill_proficiency.items():
            # Map score to a heat level (0-4)
            score = prof['score_percentage']
            heat_level = 0
            if score >= 80:
                heat_level = 4
            elif score >= 60:
                heat_level = 3
            elif score >= 40:
                heat_level = 2
            elif score >= 20:
                heat_level = 1
                
            heatmap_data.append({
                'skill_id': skill_id,
                'skill_name': prof['skill_name'],
                'score': score,
                'heat_level': heat_level
            })
        
        return {
            'radar_chart': radar_data,
            'bar_chart': bar_chart_data,
            'heatmap': heatmap_data
        }

# Helper function for Wilson score interval
def sqrt(x):
    return x ** 0.5