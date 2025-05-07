<?php

namespace App\Http\Controllers;

use App\Models\UserQuizResult;
use App\Models\Quiz;
use Illuminate\Http\Request;

class QuizResultController extends Controller
{
    public function index(Request $request)
    {
        $user = $request->user();
        
        $results = UserQuizResult::with(['quiz.topic'])
            ->where('user_id', $user->id)
            ->orderBy('completed_at', 'desc')
            ->paginate(10);
        
        return response()->json($results);
    }
    
    public function show(UserQuizResult $result, Request $request)
    {
        // Check if result belongs to user
        if ($result->user_id !== $request->user()->id && !$request->user()->is_admin) {
            return response()->json(['error' => 'Unauthorized'], 403);
        }
        
        // Load relationships
        $result->load(['quiz.topic']);
        
        // Get user responses for the quiz
        $responses = $request->user()->responses()
            ->whereHas('question', function($query) use ($result) {
                $query->whereHas('chapter', function($query) use ($result) {
                    $query->where('quiz_id', $result->quiz_id);
                });
            })
            ->with(['question'])
            ->get();
        
        // Format result for frontend display
        $formattedResult = [
            'id' => $result->id,
            'quiz_id' => $result->quiz_id,
            'quiz_title' => $result->quiz->title,
            'topic_name' => $result->quiz->topic->name,
            'total_points' => $result->total_points,
            'points_earned' => $result->points_earned,
            'percentage_score' => $result->percentage_score,
            'chapter_scores' => $result->chapter_scores,
            'skill_gaps' => $result->skill_gaps,
            'feedback' => $result->feedback,
            'completed_at' => $result->completed_at->format('Y-m-d H:i:s'),
            'responses' => []
        ];
        
        foreach ($responses as $response) {
            $formattedResult['responses'][] = [
                'question_id' => $response->question_id,
                'question_content' => $response->question->content,
                'question_type' => $response->question->type,
                'response' => $response->response,
                'is_correct' => $response->is_correct,
                'points_earned' => $response->points_earned,
                'correct_answer' => $response->question->correct_answer,
                'explanation' => $response->question->explanation
            ];
        }
        
        return response()->json($formattedResult);
    }
}