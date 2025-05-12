<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\SpacedRepetitionSchedule;
use App\Models\Skill;
use App\Services\AgentService;
use Auth;
use Carbon\Carbon;

class SpacedRepetitionController extends Controller
{
    protected $agentService;
    
    public function __construct(AgentService $agentService)
    {
        $this->agentService = $agentService;
    }
    
    /**
     * Display the spaced repetition dashboard
     */
    public function index()
    {
        $user = Auth::user();
        
        // Get due repetitions
        $dueRepetitions = SpacedRepetitionSchedule::where('user_id', $user->id)
            ->where('status', 'scheduled')
            ->where('scheduled_date', '<=', now())
            ->with('skill')
            ->orderBy('scheduled_date')
            ->get();
            
        // Get upcoming repetitions
        $upcomingRepetitions = SpacedRepetitionSchedule::where('user_id', $user->id)
            ->where('status', 'scheduled')
            ->where('scheduled_date', '>', now())
            ->with('skill')
            ->orderBy('scheduled_date')
            ->take(10)
            ->get();
            
        // Get completed repetitions stats
        $completedCount = SpacedRepetitionSchedule::where('user_id', $user->id)
            ->where('status', 'completed')
            ->count();
            
        // Group skills by proficiency level
        $skillProficiency = $this->getSkillProficiencyLevels($user->id);
        
        return view('spaced-repetition.index', [
            'dueRepetitions' => $dueRepetitions,
            'upcomingRepetitions' => $upcomingRepetitions,
            'completedCount' => $completedCount,
            'skillProficiency' => $skillProficiency
        ]);
    }
    
    /**
     * Show a specific repetition session
     */
    public function showSession($id)
    {
        $schedule = SpacedRepetitionSchedule::findOrFail($id);
        
        // Authorization check
        if ($schedule->user_id !== Auth::id()) {
            abort(403);
        }
        
        // Get skill details
        $skill = Skill::findOrFail($schedule->skill_id);
        
        // Generate practice questions for this session
        $questions = $this->generatePracticeQuestions($schedule);
        
        return view('spaced-repetition.session', [
            'schedule' => $schedule,
            'skill' => $skill,
            'questions' => $questions
        ]);
    }
    
    /**
     * Complete a repetition session
     */
    public function completeSession(Request $request, $id)
    {
        $request->validate([
            'performance_rating' => 'required|integer|min:0|max:5',
        ]);
        
        $schedule = SpacedRepetitionSchedule::findOrFail($id);
        
        // Authorization check
        if ($schedule->user_id !== Auth::id()) {
            abort(403);
        }
        
        $performanceRating = $request->input('performance_rating');
        
        // Call the API to complete the repetition
        $response = $this->agentService->call('spaced-repetition/complete', [
            'schedule_id' => $id,
            'performance_rating' => $performanceRating
        ]);
        
        if ($response['status'] === 'success') {
            $nextSchedule = $response['next_schedule'];
            
            return redirect()->route('spaced-repetition.index')
                ->with('success', "Session completed! Next review scheduled for " . 
                    Carbon::parse($nextSchedule['scheduled_date'])->format('M d, Y'));
        }
        
        return redirect()->route('spaced-repetition.index')
            ->with('error', 'Failed to complete session: ' . ($response['message'] ?? 'Unknown error'));
    }
    
    /**
     * Get skill proficiency levels based on repetition history
     */
    private function getSkillProficiencyLevels($userId)
    {
        $skills = Skill::all();
        $proficiencyLevels = [];
        
        foreach ($skills as $skill) {
            // Get completed repetitions for this skill
            $completedRepetitions = SpacedRepetitionSchedule::where('user_id', $userId)
                ->where('skill_id', $skill->id)
                ->where('status', 'completed')
                ->orderBy('completed_at', 'desc')
                ->get();
                
            if ($completedRepetitions->count() > 0) {
                // Calculate average performance rating from recent sessions
                $recentRepetitions = $completedRepetitions->take(5);
                $avgRating = $recentRepetitions->avg('performance_rating');
                
                // Calculate proficiency level (0-100)
                $repetitionCount = $completedRepetitions->count();
                $highestRepetitionNumber = $completedRepetitions->max('repetition_number');
                
                // Combine factors: performance, number of repetitions, and highest level reached
                $proficiency = min(100, (
                    ($avgRating / 5) * 40 +  // 40% weight for performance
                    min(1, $repetitionCount / 10) * 30 +  // 30% weight for repetition count (max 10)
                    min(1, $highestRepetitionNumber / 5) * 30  // 30% weight for highest level (max 5)
                ));
                
                $proficiencyLevels[$skill->id] = [
                    'skill' => $skill,
                    'proficiency' => round($proficiency),
                    'repetition_count' => $repetitionCount,
                    'highest_repetition' => $highestRepetitionNumber,
                    'avg_rating' => round($avgRating, 1)
                ];
            } else {
                // No history for this skill
                $proficiencyLevels[$skill->id] = [
                    'skill' => $skill,
                    'proficiency' => 0,
                    'repetition_count' => 0,
                    'highest_repetition' => 0,
                    'avg_rating' => 0
                ];
            }
        }
        
        return $proficiencyLevels;
    }
    
    /**
     * Generate practice questions for a repetition session
     */
    private function generatePracticeQuestions($schedule)
    {
        // Call the backend API to generate targeted practice questions
        $response = $this->agentService->call('quiz-generator/practice-questions', [
            'user_id' => $schedule->user_id,
            'skill_id' => $schedule->skill_id,
            'repetition_number' => $schedule->repetition_number,
            'count' => 5  // Number of questions to generate
        ]);
        
        if ($response['status'] === 'success' && isset($response['questions'])) {
            return $response['questions'];
        }
        
        // Fallback to generic questions if API call fails
        return [];
    }
}