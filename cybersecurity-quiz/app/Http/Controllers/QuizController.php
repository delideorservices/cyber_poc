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
use Illuminate\Support\Facades\Auth;

class QuizController extends Controller
{
    public function index(Request $request)
    {
        $user = $request->user();
        $quizzes = Quiz::with(['topic'])
            // ->where('user_id', $user->id)
            ->orderBy('created_at', 'desc')
            ->paginate(10);
            
        return response()->json($quizzes);
    }
    
    public function show(Quiz $quiz, Request $request)
    {
        // Check if quiz belongs to user
        // if ($quiz->user_id !== $request->user()->id && !$request->user()->is_admin) {
        //     return response()->json(['error' => 'Unauthorized'], 403);
        // }
        // dd($quiz);
        // Load quiz relationships
        $quiz->load(['chapters.questions', 'topic', 'sector', 'role']);
        
        // Format quiz for frontend display
        $formattedQuiz = [
            'id' => $quiz->id,
            'title' => $quiz->title,
            'description' => $quiz->description,
            'topic' => $quiz->topic->name,
            'difficulty_level' => $quiz->difficulty_level,
            'created_at' => $quiz->created_at 
                ? $quiz->created_at->format('Y-m-d H:i:s') 
                : null,
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
                    'correct_answer' => $question->correct_answer, // Added correct answer
                    'explanation' => $question->explanation, // Added explanation
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
        // dd(Auth::user());
        // Prepare data for AI backend
        $requestData = [
            'user_id' => $user->id, 
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
            // dd(config('services.ai_backend.url') . '/api/agents/register');
            if ($response->successful()) {
                $result = $response->json();
                
                // Check if the result indicates success and contains a quiz_id
                if ($result['status'] === 'success' && isset($result['quiz_id'])) {
                    $quiz_id = $result['quiz_id'];
                    
                    // Try to find the quiz in our database (it may have been saved by the Python backend)
                    $quiz = Quiz::find($quiz_id);
                    
                    if ($quiz) {
                        // Quiz already exists in our database
                        return response()->json([
                            'status' => 'success',
                            'quiz_id' => $quiz->id,
                            'message' => 'Quiz retrieved successfully'
                        ]);
                    } else {
                        // Quiz doesn't exist in our database yet, create it
                        $quiz = Quiz::create([
                            'id' => $quiz_id, // Use the same ID provided by the backend
                            'title' => $result['quiz_title'] ?? 'Cybersecurity Quiz',
                            'description' => '',
                            'user_id' => $user->id,
                            'topic_id' => $request->topic_id,
                            'difficulty_level' => 3,
                        ]);
                        
                        // If metadata is available, try to create chapters and questions
                        if (isset($result['complete_quiz'])) {
                            $completeQuiz = $result['complete_quiz'];
                            
                            // Create chapters and questions
                            $sequence = 1;
                            foreach ($completeQuiz['chapters'] ?? [] as $chapterData) {
                                $chapter = Chapter::create([
                                    'quiz_id' => $quiz->id,
                                    'title' => $chapterData['title'] ?? "Chapter $sequence",
                                    'description' => $chapterData['description'] ?? '',
                                    'sequence' => $sequence++,
                                ]);
                                
                                $questionSeq = 1;
                                foreach ($chapterData['questions'] ?? [] as $questionData) {
                                    Question::create([
                                        'chapter_id' => $chapter->id,
                                        'type' => $questionData['type'] ?? 'mcq',
                                        'content' => $questionData['content'] ?? '',
                                        'options' => isset($questionData['options']) ? json_encode($questionData['options']) : '[]',
                                        'correct_answer' => $questionData['correct_answer'] ?? '',
                                        'explanation' => $questionData['explanation'] ?? '',
                                        'sequence' => $questionSeq++,
                                        'points' => $questionData['points'] ?? 1,
                                    ]);
                                }
                            }
                        }
                        
                        return response()->json([
                            'status' => 'success',
                            'quiz_id' => $quiz->id,
                            'message' => 'Quiz generated and saved successfully'
                        ]);
                    }
                } else {
                    // Response doesn't match expected format - create a basic quiz
                    $quiz = Quiz::create([
                        'title' => $result['quiz_title'] ?? 'Cybersecurity Quiz',
                        'description' => '',
                        'user_id' => $user->id,
                        'topic_id' => $request->topic_id,
                        'difficulty_level' => 3,
                    ]);
                    
                    return response()->json([
                        'status' => 'success',
                        'quiz_id' => $quiz->id,
                        'message' => 'Basic quiz created from available data'
                    ]);
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
                // Store the quiz result in the database
                $quizResult = new UserQuizResult([
                    'user_id' => $request->user()->id,
                    'quiz_id' => $quiz->id,
                    'score' => $result['percentage_score'],
                    'feedback' => $result['feedback'],
                    'external_result_id' => $result['result_id']
                ]);
                $quizResult->save();
                
                // After successful quiz submission, trigger analytics process
                try {
                    // Trigger analytics processing
                    $analyticsResponse = Http::post(config('services.agents.url') . '/api/agent/analytics_agent', [
                        'user_id' => $request->user()->id,
                        'data' => [
                            'action' => 'process_quiz_results',
                            'quiz_id' => $quiz->id,
                            'result_id' => $result['result_id']
                        ]
                    ]);
                    
                    // If analytics successful, trigger learning plan generation
                    if ($analyticsResponse->successful()) {
                        Http::post(config('services.agents.url') . '/api/agent/learning_plan_agent', [
                            'user_id' => $request->user()->id,
                            'data' => [
                                'action' => 'generate_plan',
                                'quiz_id' => $quiz->id,
                                'result_id' => $result['result_id']
                            ]
                        ]);
                    }
                } catch (\Exception $e) {
                    // Log the error but don't fail the quiz submission
                    Log::error("Failed to trigger analytics: " . $e->getMessage());
                }
                
                // Original success response
                return response()->json([
                    'status' => 'success',
                    'result_id' => $result['result_id'],
                    'quiz_result_id' => $quizResult->id,
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
