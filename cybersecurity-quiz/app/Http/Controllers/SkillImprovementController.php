<?php

namespace App\Http\Controllers;
use App\Http\Controllers\BaseApiController;

use Illuminate\Http\Request;
use App\Services\AgentService;
use App\Models\Skill;
use Illuminate\Support\Facades\Auth;

class SkillImprovementController extends BaseApiController
{
    protected $agentService;
    
    public function __construct(AgentService $agentService)
    {
        $this->agentService = $agentService;
    }
    
    /**
     * Get skill improvement data for a specific skill
     * 
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function getSkillImprovement($id)
    {
        $user = Auth::user();
        $skill = Skill::findOrFail($id);
        
        // Get skill improvement data
        $result = $this->agentService->executeAgent('skill_improvement_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'get_improvement_data',
                'skill_id' => $id
            ]
        ]);
        
        if (!$result['success']) {
            return $this->errorResponse(
                'Failed to retrieve skill improvement data',
                $result['details'] ?? null,
                500
            );
        }
        
        return $this->successResponse(array_merge(
            $result['data'],
            ['skill' => $skill]
        ));
    }
    
    /**
     * Start a practice session for a skill
     * 
     * @param Request $request
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
 public function startPracticeSession(Request $request, $id)
{
    $user = Auth::user();
    $skill = Skill::findOrFail($id);
    
    $validated = $request->validate([
        'difficulty' => 'sometimes|integer|min:1|max:5',
        'question_count' => 'sometimes|integer|min:3|max:20',
        'adaptive' => 'sometimes|boolean'
    ]);
    
    // Set default values
    $difficulty = $validated['difficulty'] ?? 3;
    $questionCount = $validated['question_count'] ?? 5;
    $adaptive = $validated['adaptive'] ?? true;
    
    // Get user's current skill proficiency from analytics
    $skillAnalytic = SkillAnalytic::where('user_id', $user->id)
                                 ->where('skill_id', $id)
                                 ->first();
    
    // If adaptive mode is enabled and analytics exist, adjust difficulty based on proficiency
    if ($adaptive && $skillAnalytic) {
        // Convert proficiency score (0-100) to difficulty level (1-5)
        // Higher proficiency = higher difficulty to challenge the user
        if ($skillAnalytic->proficiency_score >= 80) {
            $difficulty = 5; // Expert
        } elseif ($skillAnalytic->proficiency_score >= 60) {
            $difficulty = 4; // Advanced
        } elseif ($skillAnalytic->proficiency_score >= 40) {
            $difficulty = 3; // Intermediate
        } elseif ($skillAnalytic->proficiency_score >= 20) {
            $difficulty = 2; // Easy
        } else {
            $difficulty = 1; // Beginner
        }
    }
    
    // Get previous practice sessions to maintain progression
    $previousSessions = SkillImprovementSession::where('user_id', $user->id)
                                              ->where('skill_id', $id)
                                              ->orderBy('created_at', 'desc')
                                              ->take(3)
                                              ->get();
    
    // Start a practice session
    $result = $this->agentService->executeAgent('skill_improvement_agent', [
        'user_id' => $user->id,
        'data' => [
            'action' => 'start_practice',
            'skill_id' => $id,
            'skill_name' => $skill->name,
            'difficulty' => $difficulty,
            'question_count' => $questionCount,
            'adaptive' => $adaptive,
            'previous_sessions' => $previousSessions->toArray(),
            'user_context' => [
                'sector_id' => $user->sector_id,
                'role_id' => $user->role_id,
                'years_experience' => $user->years_experience
            ]
        ]
    ]);
    
    if (!$result['success']) {
        return $this->errorResponse(
            'Failed to start practice session',
            $result['details'] ?? null,
            500
        );
    }
    
    // Create a new session record
    $session = new SkillImprovementSession([
        'user_id' => $user->id,
        'skill_id' => $id,
        'difficulty_level' => $difficulty,
        'question_count' => $questionCount,
        'is_adaptive' => $adaptive,
        'status' => 'in_progress',
        'session_data' => $result['data']['session_data'] ?? [],
        'external_session_id' => $result['data']['session_id'] ?? null
    ]);
    $session->save();
    
    return $this->successResponse([
        'session_id' => $session->id,
        'session_data' => $result['data'],
        'difficulty_level' => $difficulty,
        'is_adaptive' => $adaptive
    ]);
}
    
    /**
     * Submit a response for a practice question
     * 
     * @param Request $request
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function submitPracticeResponse(Request $request, $id)
    {
        $user = Auth::user();
        
        $validated = $request->validate([
            'question_id' => 'required|integer',
            'answer' => 'required',
            'time_spent' => 'sometimes|integer'
        ]);
        
        // Submit practice response
        $result = $this->agentService->executeAgent('skill_improvement_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'submit_response',
                'practice_id' => $id,
                'question_id' => $validated['question_id'],
                'answer' => $validated['answer'],
                'time_spent' => $validated['time_spent'] ?? null
            ]
        ]);
        
        if (!$result['success']) {
            return $this->errorResponse(
                'Failed to submit practice response',
                $result['details'] ?? null,
                500
            );
        }
        
        return $this->successResponse($result['data']);
    }
    
    /**
     * Complete a practice session
     * 
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function completePracticeSession($id)
    {
        $user = Auth::user();
        
        // Complete practice session
        $result = $this->agentService->executeAgent('skill_improvement_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'complete_practice',
                'practice_id' => $id
            ]
        ]);
        
        if (!$result['success']) {
            return $this->errorResponse(
                'Failed to complete practice session',
                $result['details'] ?? null,
                500
            );
        }
        
        return $this->successResponse($result['data']);
    }
    

  public function getDueRepetitions()
{
    $user = Auth::user();
    
    // Call skill improvement agent to get due repetitions
    $result = $this->agentService->executeAgent('skill_improvement_agent', [
        'user_id' => $user->id,
        'data' => [
            'action' => 'get_due_repetitions',
            'algorithm' => 'sm2' // Specify SuperMemo-2 algorithm
        ]
    ]);
    
    if (!$result['success']) {
        return $this->errorResponse(
            'Failed to retrieve due repetitions',
            $result['details'] ?? null,
            500
        );
    }
    
    // Process items for frontend display
    $dueItems = [];
    if (isset($result['data']['due_items']) && is_array($result['data']['due_items'])) {
        foreach ($result['data']['due_items'] as $item) {
            // Create repetition tracking entries if not already created
            $repetition = SpacedRepetitionItem::firstOrCreate(
                [
                    'user_id' => $user->id, 
                    'content_id' => $item['content_id'],
                    'content_type' => $item['content_type']
                ],
                [
                    'easiness_factor' => $item['easiness_factor'] ?? 2.5,
                    'interval' => $item['interval'] ?? 1,
                    'repetition_count' => $item['repetition_count'] ?? 0,
                    'due_date' => now(),
                    'content_data' => $item['content_data'] ?? []
                ]
            );
            
            $dueItems[] = [
                'id' => $repetition->id,
                'content' => $repetition->content_data,
                'type' => $repetition->content_type,
                'due_date' => $repetition->due_date->format('Y-m-d')
            ];
        }
    }
    
    return $this->successResponse([
        'due_items' => $dueItems,
        'total_items' => count($dueItems),
        'next_review_date' => isset($result['data']['next_review_date']) 
            ? $result['data']['next_review_date'] 
            : now()->addDay()->format('Y-m-d')
    ]);
}


public function completeRepetition(Request $request, $id)
{
    $user = Auth::user();
    
    $validated = $request->validate([
        'performance_rating' => 'required|integer|min:0|max:5'
    ]);
    
    $repetitionItem = SpacedRepetitionItem::where('user_id', $user->id)
                                        ->where('id', $id)
                                        ->firstOrFail();
    
    // Call skill improvement agent to update the spaced repetition algorithm
    $result = $this->agentService->executeAgent('skill_improvement_agent', [
        'user_id' => $user->id,
        'data' => [
            'action' => 'update_repetition',
            'item_id' => $repetitionItem->id,
            'content_id' => $repetitionItem->content_id,
            'content_type' => $repetitionItem->content_type,
            'performance_rating' => $validated['performance_rating'],
            'current_easiness_factor' => $repetitionItem->easiness_factor,
            'current_interval' => $repetitionItem->interval,
            'current_repetition_count' => $repetitionItem->repetition_count,
            'algorithm' => 'sm2'
        ]
    ]);
    
    if (!$result['success']) {
        return $this->errorResponse(
            'Failed to update repetition item',
            $result['details'] ?? null,
            500
        );
    }
    
    // Update the repetition item with new values
    $repetitionItem->easiness_factor = $result['data']['new_easiness_factor'];
    $repetitionItem->interval = $result['data']['new_interval'];
    $repetitionItem->repetition_count = $repetitionItem->repetition_count + 1;
    $repetitionItem->performance_history = array_merge(
        $repetitionItem->performance_history ?? [], 
        [$validated['performance_rating']]
    );
    $repetitionItem->due_date = now()->addDays($result['data']['new_interval']);
    $repetitionItem->last_reviewed_at = now();
    $repetitionItem->save();
    
    return $this->successResponse([
        'updated_item' => $repetitionItem,
        'next_review_date' => $repetitionItem->due_date->format('Y-m-d'),
        'message' => 'Repetition completed successfully'
    ]);
}
    
}