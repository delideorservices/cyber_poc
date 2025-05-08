<?php

namespace App\Http\Controllers;

use App\Models\Quiz;
use App\Models\Chapter;
use App\Models\Question;
use App\Models\User;
use App\Models\UserResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Validator;
use Carbon\Carbon;
class QuizController extends Controller
{
    public function index(Request $request)
    {
        $user = $request->user();
        $quizzes = Quiz::with(['topic'])
            ->where('user_id', $user->id)
            ->orderBy('created_at', 'desc')
            ->paginate(10);
            
        return response()->json($quizzes);
    }
    
    public function show(Quiz $quiz, Request $request)
    {
        // Check if quiz belongs to user
        if ($quiz->user_id !== $request->user()->id && !$request->user()->is_admin) {
            return response()->json(['error' => 'Unauthorized'], 403);
        }
        
        // Load quiz relationships
        $quiz->load(['chapters.questions', 'topic', 'sector', 'role']);
        
        // Format quiz for frontend display
        $formattedQuiz = [
            'id' => $quiz->id,
            'title' => $quiz->title,
            'description' => $quiz->description,
            'topic' => $quiz->topic->name,
            'difficulty_level' => $quiz->difficulty_level,
            'created_at' => $quiz->created_at->format('Y-m-d H:i:s'),
            'chapters' => []
        ];
        
        foreach ($quiz->chapters as $chapter) {
            $formattedChapter = [
                'id' => $chapter->id,
                'title' => $chapter->title,
                'description' => $chapter->description,
                'sequence' => $chapter->sequence,
                'questions' => []
            ];
            
            foreach ($chapter->questions as $question) {
                $formattedQuestion = [
                    'id' => $question->id,
                    'type' => $question->type,
                    'content' => $question->content,
                    'options' => $question->options,
                    'sequence' => $question->sequence,
                    'points' => $question->points
                ];
                
                $formattedChapter['questions'][] = $formattedQuestion;
            }
            
            $formattedQuiz['chapters'][] = $formattedChapter;
        }
        
        return response()->json($formattedQuiz);
    }
    
    public function generate(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'topic_id' => 'required|exists:topics,id',
            'skills' => 'sometimes|array',
            'certifications' => 'sometimes|array',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }
        
        $user = $request->user();
        // dd($user);
        // Prepare data for AI backend
        $requestData = [
            'name' => $user->name,
            'email' => $user->email,
            'gender' => $user->gender,
            'age' => $user->age,
            'sector_id' => $user->sector_id,
            'role_id' => $user->role_id,
            'years_experience' => $user->years_experience,
            'learning_goal' => $user->learning_goal,
            'preferred_language' => $user->preferred_language,
            'topic_id' => $request->topic_id,
            'skills' => [],
            'certifications' => []
        ];
        
        // Add user skills
        foreach ($user->skills as $skill) {
            $requestData['skills'][] = [
                'id' => $skill->id,
                'proficiency' => $skill->pivot->proficiency_level
            ];
        }
        
        // Add user certifications
        foreach ($user->certifications as $cert) {
            $requestData['certifications'][] = [
                'id' => $cert->id,
                'obtained_date' => $cert->pivot->obtained_date 
                    ? Carbon::parse($cert->pivot->obtained_date)->format('Y-m-d') 
                    : null,

                'expiry_date' => $cert->pivot->expiry_date 
                    ? Carbon::parse($cert->pivot->expiry_date)->format('Y-m-d') 
                    : null,
            ];
        }
        
        // Call AI backend to generate quiz
        try {
            $response = Http::timeout(300)->post(config('services.ai_backend.url') . '/api/agents/register', $requestData);
            dd($response->json());
            if ($response->successful()) {
                $result = $response->json();
                
                if (isset($result['quiz'])) {
                    $quizData = $result['quiz'];
                
                    // 1️⃣ Save Quiz
                    $quiz = Quiz::create([
                        'title' => $quizData['title'],
                        'description' => $quizData['description'] ?? '',
                        'user_id' => $user->id,
                        'topic_id' => $request->topic_id,
                        'difficulty_level' => $quizData['difficulty_level'] ?? 1,
                    ]);
                
                    // 2️⃣ Save Chapters + Questions
                    $sequence = 1;
                    foreach ($quizData['chapters'] as $chapterData) {
                        $chapter = Chapter::create([
                            'quiz_id' => $quiz->id,
                            'title' => $chapterData['title'],
                            'description' => $chapterData['description'] ?? '',
                            'sequence' => $sequence++,
                        ]);
                
                        $questionSeq = 1;
                        foreach ($chapterData['questions'] as $questionData) {
                            Question::create([
                                'chapter_id' => $chapter->id,
                                'type' => $questionData['type'],
                                'content' => $questionData['content'],
                                'options' => isset($questionData['options']) ? json_encode($questionData['options']) : null,
                                'correct_answer' => $questionData['correct_answer'] ?? null,
                                'explanation' => $questionData['explanation'] ?? null,
                                'sequence' => $questionSeq++,
                                'points' => $questionData['points'] ?? 1,
                            ]);
                        }
                    }
                
                    return response()->json([
                        'status' => 'success',
                        'quiz_id' => $quiz->id,
                        'message' => 'Quiz generated and saved successfully'
                    ]);
                }
                
                else {
                    // Something went wrong
                    return response()->json([
                        'status' => 'error',
                        'message' => 'Failed to generate quiz: Invalid response format'
                    ], 500);
                }
            } else {
                // Error response from AI backend
                return response()->json([
                    'status' => 'error',
                    'message' => 'Failed to generate quiz: ' . ($response->json()['detail'] ?? 'Unknown error')
                ], $response->status());
            }
        } catch (\Exception $e) {
            // Exception during API call
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to communicate with AI backend: ' . $e->getMessage()
            ], 500);
        }
    }
    
    public function submit(Request $request, Quiz $quiz)
    {
        // Check if quiz belongs to user
        if ($quiz->user_id !== $request->user()->id) {
            return response()->json(['error' => 'Unauthorized'], 403);
        }
        
        $validator = Validator::make($request->all(), [
            'responses' => 'required|array',
            'responses.*.question_id' => 'required|exists:questions,id',
            'responses.*.answer' => 'required',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }
        
        // Prepare data for AI backend
        $requestData = [
            'user_id' => $request->user()->id,
            'quiz_id' => $quiz->id,
            'responses' => $request->responses
        ];
        
        // Call AI backend to evaluate quiz
        try {
            $response = Http::post(config('services.ai_backend.url') . '/api/agents/evaluate', $requestData);
            
            if ($response->successful()) {
                $result = $response->json();
                
                if (isset($result['result_id'])) {
                    // Quiz successfully evaluated
                    return response()->json([
                        'status' => 'success',
                        'result_id' => $result['result_id'],
                        'percentage_score' => $result['percentage_score'],
                        'feedback' => $result['feedback']
                    ]);
                } else {
                    // Something went wrong
                    return response()->json([
                        'status' => 'error',
                        'message' => 'Failed to evaluate quiz: Invalid response format'
                    ], 500);
                }
            } else {
                // Error response from AI backend
                return response()->json([
                    'status' => 'error',
                    'message' => 'Failed to evaluate quiz: ' . ($response->json()['detail'] ?? 'Unknown error')
                ], $response->status());
            }
        } catch (\Exception $e) {
            // Exception during API call
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to communicate with AI backend: ' . $e->getMessage()
            ], 500);
        }
    }
}