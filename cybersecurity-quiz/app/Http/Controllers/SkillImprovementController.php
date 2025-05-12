<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\SkillImprovementSession;
use App\Models\SpacedRepetitionSchedule;
use App\Models\Skill;
use App\Models\Question;
use App\Models\UserResponse;
use App\Services\AgentService;
use Auth;
use DB;

class SkillImprovementController extends Controller
{
    protected $agentService;
    
    public function __construct(AgentService $agentService)
    {
        $this->agentService = $agentService;
    }
    
    /**
     * Display skill improvement dashboard
     */
    public function index()
    {
        $user = Auth::user();
        
        // Get user's skill gaps
        $skillGaps = DB::table('user_quiz_results')
            ->where('user_id', $user->id)
            ->whereNotNull('skill_gaps')
            ->orderBy('created_at', 'desc')
            ->first();
            
        $skillGaps = $skillGaps ? json_decode($skillGaps->skill_gaps, true) : [];
        
        // Get active improvement sessions
        $sessions = SkillImprovementSession::where('user_id', $user->id)
            ->orderBy('created_at', 'desc')
            ->take(5)
            ->get();
            
        // Get upcoming spaced repetition activities
        $upcomingRepetitions = SpacedRepetitionSchedule::where('user_id', $user->id)
            ->where('status', 'scheduled')
            ->where('scheduled_date', '>=', now())
            ->orderBy('scheduled_date', 'asc')
            ->take(5)
            ->get();
            
        return view('skills.improvement.index', [
            'skillGaps' => $skillGaps,
            'sessions' => $sessions,
            'upcomingRepetitions' => $upcomingRepetitions
        ]);
    }
    
    /**
     * Display a specific improvement session
     */
    public function showSession($id)
    {
        $session = SkillImprovementSession::findOrFail($id);
        
        // Authorization check
        if ($session->user_id !== Auth::id()) {
            abort(403);
        }
        
        $activities = json_decode($session->activities, true);
        
        return view('skills.improvement.session', [
            'session' => $session,
            'activities' => $activities
        ]);
    }
    
    /**
     * Start a new improvement session
     */
    public function startSession(Request $request)
    {
        $request->validate([
            'skills' => 'required|array',
            'skills.*' => 'exists:skills,id'
        ]);
        
        $user = Auth::user();
        $skillIds = $request->input('skills');
        
        // Get full skill information
        $skills = Skill::whereIn('id', $skillIds)->get()->toArray();
        
        // Call the Skill Improvement Agent
        $response = $this->agentService->callAgent('SkillImprovementAgent', [
            'user_id' => $user->id,
            'specific_skills' => $skills
        ]);
        
        if ($response['status'] === 'success') {
            return redirect()->route('skills.improvement.session', $response['session_id'])
                ->with('success', 'Skill improvement session created successfully');
        }
        
        return redirect()->route('skills.improvement')
            ->with('error', 'Failed to create improvement session: ' . ($response['message'] ?? 'Unknown error'));
    }
    
    /**
     * Retry a specific question
     */
    public function retryQuestion($questionId, Request $request)
    {
        $question = Question::findOrFail($questionId);
        $user = Auth::user();
        
        $request->validate([
            'response' => 'required',
        ]);
        
        $userResponse = $request->input('response');
        $correctAnswer = json_decode($question->correct_answer, true);
        
        // Check if response is correct
        $isCorrect = $this->checkResponse($question->type, $userResponse, $correctAnswer);
        
        // Calculate points earned
        $pointsEarned = $isCorrect ? $question->points : 0;
        
        // Record the response
        UserResponse::create([
            'user_id' => $user->id,
            'question_id' => $question->id,
            'response' => json_encode($userResponse),
            'is_correct' => $isCorrect,
            'points_earned' => $pointsEarned,
            'answered_at' => now()
        ]);
        
        // Update session progress if session_id is provided
        if ($request->has('session_id')) {
            $sessionId = $request->input('session_id');
            $this->updateSessionProgress($sessionId, $questionId, $isCorrect);
        }
        
        return response()->json([
            'success' => true,
            'is_correct' => $isCorrect,
            'points_earned' => $pointsEarned,
            'explanation' => $question->explanation,
            'correct_answer' => $correctAnswer
        ]);
    }
    
    /**
     * Show improvement progress
     */
    public function progress()
    {
        $user = Auth::user();
        
        // Get completed sessions
        $completedSessions = SkillImprovementSession::where('user_id', $user->id)
            ->where('status', 'completed')
            ->orderBy('created_at', 'desc')
            ->get();
            
        // Get skill improvement metrics
        $skillMetrics = $this->calculateSkillImprovementMetrics($user->id);
        
        return view('skills.improvement.progress', [
            'completedSessions' => $completedSessions,
            'skillMetrics' => $skillMetrics
        ]);
    }
    
    /**
     * Helper function to check if a response is correct
     */
    private function checkResponse($questionType, $userResponse, $correctAnswer)
    {
        switch ($questionType) {
            case 'mcq':
                return $userResponse == $correctAnswer;
                
            case 'true_false':
                return $userResponse == $correctAnswer;
                
            case 'fill_blank':
                // Case-insensitive comparison for fill in the blank
                return strtolower($userResponse) == strtolower($correctAnswer);
                
            case 'drag_drop':
                // For drag and drop, check if arrays match
                if (is_array($userResponse) && is_array($correctAnswer)) {
                    return count(array_diff($userResponse, $correctAnswer)) === 0 &&
                           count(array_diff($correctAnswer, $userResponse)) === 0;
                }
                return false;
                
            default:
                return false;
        }
    }
    
    /**
     * Update session progress
     */
    private function updateSessionProgress($sessionId, $questionId, $isCorrect)
    {
        $session = SkillImprovementSession::findOrFail($sessionId);
        
        // Only process if user authorized
        if ($session->user_id !== Auth::id()) {
            return;
        }
        
        $activities = json_decode($session->activities, true);
        $updated = false;
        
        // Update question status in activities
        foreach ($activities as &$activity) {
            if (isset($activity['questions'])) {
                foreach ($activity['questions'] as &$question) {
                    if ($question['id'] == $questionId) {
                        $question['retried'] = true;
                        $question['successful'] = $isCorrect;
                        $updated = true;
                        break;
                    }
                }
            }
            
            // Also update success metrics
            if ($updated) {
                $totalQuestions = count($activity['questions']);
                $retriedQuestions = count(array_filter($activity['questions'], function($q) {
                    return isset($q['retried']) && $q['retried'];
                }));
                $successfulRetries = count(array_filter($activity['questions'], function($q) {
                    return isset($q['successful']) && $q['successful'];
                }));
                
                $activity['progress'] = [
                    'total' => $totalQuestions,
                    'retried' => $retriedQuestions,
                    'successful' => $successfulRetries,
                    'completion_percentage' => $totalQuestions > 0 ? 
                        round(($retriedQuestions / $totalQuestions) * 100) : 0,
                    'success_rate' => $retriedQuestions > 0 ? 
                        round(($successfulRetries / $retriedQuestions) * 100) : 0
                ];
                
                break;
            }
        }
        
        if ($updated) {
            $session->activities = json_encode($activities);
            
            // Check if all questions have been retried
            $allRetried = true;
            foreach ($activities as $activity) {
                if (isset($activity['questions'])) {
                    foreach ($activity['questions'] as $question) {
                        if (!isset($question['retried']) || !$question['retried']) {
                            $allRetried = false;
                            break 2;
                        }
                    }
                }
            }
            
            if ($allRetried) {
                $session->status = 'completed';
                $session->completed_at = now();
            }
            
            $session->save();
        }
    }
    
    /**
     * Calculate skill improvement metrics
     */
    private function calculateSkillImprovementMetrics($userId)
    {
        $skills = Skill::all()->keyBy('id');
        $metrics = [];
        
        // Get all user responses
        $responses = UserResponse::where('user_id', $userId)
            ->orderBy('answered_at', 'asc')
            ->get();
            
        // Group responses by skill and calculate improvement
        foreach ($responses as $response) {
            $question = Question::with(['chapter.quiz.topic.skills'])->find($response->question_id);
            
            if (!$question || !$question->chapter || !$question->chapter->quiz) {
                continue;
            }
            
            $topicSkills = $question->chapter->quiz->topic->skills;
            
            foreach ($topicSkills as $skill) {
                $skillId = $skill->id;
                
                if (!isset($metrics[$skillId])) {
                    $metrics[$skillId] = [
                        'skill_id' => $skillId,
                        'skill_name' => $skills[$skillId]->name,
                        'total_attempts' => 0,
                        'successful_attempts' => 0,
                        'improvement_rate' => 0,
                        'time_periods' => []
                    ];
                }
                
                $metrics[$skillId]['total_attempts']++;
                if ($response->is_correct) {
                    $metrics[$skillId]['successful_attempts']++;
                }
                
                // Calculate success rate
                $metrics[$skillId]['success_rate'] = round(
                    ($metrics[$skillId]['successful_attempts'] / $metrics[$skillId]['total_attempts']) * 100
                );
                
                // Group by month for trend analysis
                $month = $response->answered_at->format('Y-m');
                
                if (!isset($metrics[$skillId]['time_periods'][$month])) {
                    $metrics[$skillId]['time_periods'][$month] = [
                        'total' => 0,
                        'successful' => 0,
                        'rate' => 0
                    ];
                }
                
                $metrics[$skillId]['time_periods'][$month]['total']++;
                if ($response->is_correct) {
                    $metrics[$skillId]['time_periods'][$month]['successful']++;
                }
                
                $metrics[$skillId]['time_periods'][$month]['rate'] = 
                    round(($metrics[$skillId]['time_periods'][$month]['successful'] / 
                          $metrics[$skillId]['time_periods'][$month]['total']) * 100);
            }
        }
        
        // Calculate improvement rates
        foreach ($metrics as &$metric) {
            $periods = array_values($metric['time_periods']);
            if (count($periods) >= 2) {
                $firstPeriod = $periods[0]['rate'];
                $lastPeriod = $periods[count($periods) - 1]['rate'];
                $metric['improvement_rate'] = $lastPeriod - $firstPeriod;
            }
        }
        
        return $metrics;
    }
}