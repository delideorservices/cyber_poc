from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.db_service import db_service

router = APIRouter()

# Models for responses
class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    topic_name: str
    difficulty_level: int
    chapters: List[Dict[str, Any]]
    user_id: int
    created_at: str

class QuizResultResponse(BaseModel):
    id: int
    quiz_id: int
    total_points: int
    points_earned: int
    percentage_score: float
    chapter_scores: Dict[str, Any]
    skill_gaps: List[str]
    feedback: str
    completed_at: str

# Routes for quiz interaction
@router.get("/user/{user_id}")
async def get_user_quizzes(user_id: int, limit: int = Query(10, ge=1, le=50)):
    """Get all quizzes for a specific user"""
    try:
        quizzes = db_service.fetch_all(
            """
            SELECT q.id, q.title, q.description, q.difficulty_level, 
                   t.name as topic_name, q.created_at,
                   COALESCE(r.percentage_score, 0) as score,
                   CASE WHEN r.id IS NOT NULL THEN true ELSE false END as completed
            FROM quizzes q
            JOIN topics t ON q.topic_id = t.id
            LEFT JOIN user_quiz_results r ON q.id = r.quiz_id AND r.user_id = q.user_id
            WHERE q.user_id = %s
            ORDER BY q.created_at DESC
            LIMIT %s
            """,
            (user_id, limit)
        )
        
        return {"quizzes": quizzes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{quiz_id}")
async def get_quiz(quiz_id: int):
    """Get a specific quiz with all questions"""
    try:
        # Get quiz data
        quiz = db_service.fetch_one(
            """
            SELECT q.*, t.name as topic_name
            FROM quizzes q
            JOIN topics t ON q.topic_id = t.id
            WHERE q.id = %s
            """,
            (quiz_id,)
        )
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Get chapters
        chapters = db_service.fetch_all(
            "SELECT * FROM chapters WHERE quiz_id = %s ORDER BY sequence",
            (quiz_id,)
        )
        
        formatted_chapters = []
        
        for chapter in chapters:
            chapter_id = chapter['id']
            
            # Get questions
            questions = db_service.fetch_all(
                "SELECT id, type, content, options, sequence, points FROM questions WHERE chapter_id = %s ORDER BY sequence",
                (chapter_id,)
            )
            
            formatted_chapters.append({
                'id': chapter['id'],
                'title': chapter['title'],
                'description': chapter['description'],
                'sequence': chapter['sequence'],
                'questions': questions
            })
        
        # Format response
        response = {
            'id': quiz['id'],
            'title': quiz['title'],
            'description': quiz['description'],
            'topic_name': quiz['topic_name'],
            'difficulty_level': quiz['difficulty_level'],
            'chapters': formatted_chapters,
            'user_id': quiz['user_id'],
            'created_at': str(quiz['created_at'])
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{user_id}")
async def get_user_results(user_id: int, limit: int = Query(10, ge=1, le=50)):
    """Get quiz results for a specific user"""
    try:
        results = db_service.fetch_all(
            """
            SELECT r.*, q.title as quiz_title, t.name as topic_name
            FROM user_quiz_results r
            JOIN quizzes q ON r.quiz_id = q.id
            JOIN topics t ON q.topic_id = t.id
            WHERE r.user_id = %s
            ORDER BY r.completed_at DESC
            LIMIT %s
            """,
            (user_id, limit)
        )
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{result_id}")
async def get_quiz_result(result_id: int):
    """Get a specific quiz result"""
    try:
        result = db_service.fetch_one(
            """
            SELECT r.*, q.title as quiz_title, t.name as topic_name
            FROM user_quiz_results r
            JOIN quizzes q ON r.quiz_id = q.id
            JOIN topics t ON q.topic_id = t.id
            WHERE r.id = %s
            """,
            (result_id,)
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))