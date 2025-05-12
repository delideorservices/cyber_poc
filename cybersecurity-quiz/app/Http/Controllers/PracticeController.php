<?php

namespace App\Http\Controllers;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Auth;
use App\Models\UserQuizResult;
use App\Models\Quiz;
use App\Models\User;
use App\Models\Skill;
use App\Models\Topic;
use App\Models\UserSkill;
class PracticeController extends Controller
{
    public function startPractice(Request $request, $userId, $skillId)
    {
        try {
            $user = User::findOrFail($userId);
            
            // Verify authorization
            $this->authorize('view', $user);
            
            $skill = Skill::findOrFail($skillId);
            
            // Get difficulty level from request (default to 3 - medium)
            $difficultyLevel = $request->input('difficulty_level', 3);
            
            // Create new practice session
            $session = new PracticeSession();
            $session->user_id = $userId;
            $session->skill_id = $skillId;
            $session->difficulty_level = $difficultyLevel;
            $session->status = 'started';
            $session->save();
            
            // Generate practice questions
            $this->generatePracticeQuestions($session);
            
            return response()->json([
                'session_id' => $session->id,
                'message' => 'Practice session created successfully'
            ]);
        } catch (\Exception $e) {
            Log::error('Error starting practice session: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to start practice session'], 500);
        }
    }
    
    /**
     * Generate practice questions for a session
     *
     * @param PracticeSession $session
     * @return void
     */
    private function generatePracticeQuestions($session)
    {
        // In a real implementation, this would call the Quiz Generator Agent
        // For now, we'll create sample questions based on difficulty
        
        // Sample question templates by type
        $questionTemplates = [
            'mcq' => [
                'content' => 'Which of the following is the best approach for {topic}?',
                'options' => [
                    '{correct_answer}',
                    '{wrong_answer_1}',
                    '{wrong_answer_2}',
                    '{wrong_answer_3}'
                ]
            ],
            'true_false' => [
                'content' => 'The statement "{statement}" is correct regarding {topic}.',
                'options' => ['true', 'false']
            ],
            'fill_blank' => [
                'content' => 'In the context of {topic}, the process of {blank} is essential for security.'
            ]
        ];
        
        // Number of questions based on difficulty
        $questionCount = 5 + $session->difficulty_level;
        
        // Create the questions
        for ($i = 0; $i < $questionCount; $i++) {
            // Select random question type
            $questionType = array_rand($questionTemplates);
            $template = $questionTemplates[$questionType];
            
            // Create new question
            $question = new PracticeQuestion();
            $question->session_id = $session->id;
            $question->type = $questionType;
            $question->content = $template['content'];
            $question->sequence = $i + 1;
            
            // Set options or other type-specific fields
            if (isset($template['options'])) {
                $question->options = json_encode($template['options']);
            }
            
            // Set correct answer placeholder
            $question->correct_answer = ($questionType === 'mcq') ? 0 : ($questionType === 'true_false' ? 'true' : '{answer}');
            
            // Set points based on difficulty
            $question->points = $session->difficulty_level * 2;
            
            $question->save();
        }
    }
    
    /**
     * Get practice session data
     *
     * @param int $sessionId
     * @return \Illuminate\Http\JsonResponse
     */
    public function getSessionData($sessionId)
    {
        try {
            $session = PracticeSession::with(['questions' => function($query) {
                $query->orderBy('sequence', 'asc');
            }])->findOrFail($sessionId);
            
            $user = Auth::user();
            
            // Verify this session belongs to the user
            if ($session->user_id !== $user->id) {
                return response()->json(['error' => 'Unauthorized access to practice session'], 403);
            }
            
            // Format question data for frontend
            $formattedQuestions = [];
            foreach ($session->questions as $question) {
                $questionData = [
                    'id' => $question->id,
                    'type' => $question->type,
                    'content' => $question->content,
                    'sequence' => $question->sequence,
                    'points' => $question->points
                ];
                
                // Add type-specific data
                if ($question->type === 'mcq' || $question->type === 'true_false') {
                    $questionData['options'] = json_decode($question->options);
                } else if ($question->type === 'drag_drop') {
                    $questionData['drag_items'] = json_decode($question->drag_items);
                    $questionData['drop_targets'] = json_decode($question->drop_targets);
                }
                
                $formattedQuestions[] = $questionData;
            }
            
            return response()->json([
                'session_id' => $session->id,
                'skill_id' => $session->skill_id,
                'difficulty_level' => $session->difficulty_level,
                'timed_practice' => $session->time_limit !== null,
                'time_limit' => $session->time_limit,
                'questions' => $formattedQuestions
            ]);
        } catch (\Exception $e) {
            Log::error('Error retrieving practice session data: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to retrieve practice session data'], 500);
        }
    }
    
    /**
     * Save practice session results
     *
     * @param Request $request
     * @param int $userId
     * @param int $sessionId
     * @return \Illuminate\Http\JsonResponse
     */
    public function savePracticeResults(Request $request, $userId, $sessionId)
    {
        try {
            $user = User::findOrFail($userId);
            
            // Verify authorization
            $this->authorize('update', $user);
            
            $session = PracticeSession::findOrFail($sessionId);
            
            // Verify this session belongs to the user
            if ($session->user_id !== $user->id) {
                return response()->json(['error' => 'Unauthorized access to practice session'], 403);
            }
            
            // Process user responses
            $responses = $request->input('responses', []);
            $totalPoints = 0;
            $earnedPoints = 0;
            
            foreach ($responses as $response) {
                if (!isset($response['question_id'])) {
                    continue;
                }
                
                $question = PracticeQuestion::find($response['question_id']);
                if (!$question || $question->session_id !== $session->id) {
                    continue;
                }
                
                // Calculate if response is correct
                $isCorrect = $this->evaluateResponse($question, $response['response']);
                
                // Calculate points earned
                $pointsEarned = $isCorrect ? $question->points : 0;
                
                // Save response
                $practiceResponse = new PracticeResponse();
                $practiceResponse->session_id = $sessionId;
                $practiceResponse->question_id = $question->id;
                $practiceResponse->response = json_encode($response['response']);
                $practiceResponse->is_correct = $isCorrect;
                $practiceResponse->points_earned = $pointsEarned;
                $practiceResponse->time_taken = $response['time_taken'] ?? 0;
                $practiceResponse->save();
                
                // Update totals
                $totalPoints += $question->points;
                $earnedPoints += $pointsEarned;
            }
            
            // Update session status
            $session->status = 'completed';
            $session->completed_at = now();
            $session->total_points = $totalPoints;
            $session->earned_points = $earnedPoints;
            $session->score_percentage = $totalPoints > 0 ? round(($earnedPoints / $totalPoints) * 100, 2) : 0;
            $session->save();
            
            // Update user skill level
            $this->updateUserSkill($userId, $session->skill_id, $session->score_percentage);
            
            return response()->json([
                'session_id' => $session->id,
                'total_points' => $totalPoints,
                'earned_points' => $earnedPoints,
                'score_percentage' => $session->score_percentage,
                'message' => 'Practice session completed successfully'
            ]);
        } catch (\Exception $e) {
            Log::error('Error saving practice results: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to save practice results'], 500);
        }
    }
    
    /**
     * Evaluate if a response is correct
     *
     * @param PracticeQuestion $question
     * @param mixed $response
     * @return bool
     */
    private function evaluateResponse($question, $response)
    {
        // This is a simplified implementation
        // In a real app, this would be more sophisticated based on question type
        
        switch ($question->type) {
            case 'mcq':
                // For MCQ, correct answer is stored as the index of the correct option
                return (int)$response === (int)$question->correct_answer;
                
            case 'true_false':
                // For true/false, compare strings
                return strtolower($response) === strtolower($question->correct_answer);
                
            case 'fill_blank':
                // For fill in the blank, check if answers match (case insensitive)
                $correctAnswers = explode('|', $question->correct_answer);
                if (is_array($response)) {
                    // Multiple blanks
                    if (count($response) !== count($correctAnswers)) {
                        return false;
                    }
                    
                    foreach ($response as $index => $answer) {
                        if (!isset($correctAnswers[$index]) || 
                            strtolower(trim($answer)) !== strtolower(trim($correctAnswers[$index]))) {
                            return false;
                        }
                    }
                    return true;
                } else {
                    // Single blank
                    return in_array(strtolower(trim($response)), array_map('strtolower', array_map('trim', $correctAnswers)));
                }
                
            case 'drag_drop':
                // For drag and drop, compare the mapping
                $correctMapping = json_decode($question->correct_answer, true);
                
                // Check if all mappings match
                foreach ($correctMapping as $targetId => $itemId) {
                    if (!isset($response[$targetId]) || $response[$targetId] !== $itemId) {
                        return false;
                    }
                }
                return true;
                
            default:
                return false;
        }
    }
    
    /**
     * Update user skill level based on practice results
     *
     * @param int $userId
     * @param int $skillId
     * @param float $scorePercentage
     * @return void
     */
    private function updateUserSkill($userId, $skillId, $scorePercentage)
    {
        // Find existing skill record or create new one
        $userSkill = UserSkill::firstOrNew([
            'user_id' => $userId,
            'skill_id' => $skillId
        ]);
        
        // If new record, set initial values
        if (!$userSkill->exists) {
            $userSkill->proficiency_level = 0;
            $userSkill->practice_count = 0;
        }
        
        // Update proficiency level
        // This is a simplified algorithm:
        // - If score > current level, increase level by 20% of the difference
        // - If score < current level, decrease level by 10% of the difference
        
        $currentLevel = $userSkill->proficiency_level;
        
        if ($scorePercentage > $currentLevel) {
            $increase = ($scorePercentage - $currentLevel) * 0.2;
            $userSkill->proficiency_level = min(100, $currentLevel + $increase);
        } else if ($scorePercentage < $currentLevel) {
            $decrease = ($currentLevel - $scorePercentage) * 0.1;
            $userSkill->proficiency_level = max(0, $currentLevel - $decrease);
        }
        
        // Increment practice count
        $userSkill->practice_count += 1;
        
        // Update last practice date
        $userSkill->last_practiced_at = now();
        
        $userSkill->save();
    }
    
    /**
     * Display practice session results
     *
     * @param int $sessionId
     * @return \Illuminate\View\View
     */
    public function showResults($sessionId)
    {
        $user = Auth::user();
        $session = PracticeSession::with(['responses', 'questions'])->findOrFail($sessionId);
        
        // Verify this session belongs to the user
        if ($session->user_id !== $user->id) {
            abort(403, 'Unauthorized access to practice results');
        }
        
        return view('practice.results', [
            'user' => $user,
            'session' => $session
        ]);
    }
}
