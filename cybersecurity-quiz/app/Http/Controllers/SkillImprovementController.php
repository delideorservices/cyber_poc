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
            'question_count' => 'sometimes|integer|min:3|max:20'
        ]);
        
        // Set default values
        $difficulty = $validated['difficulty'] ?? 3;
        $questionCount = $validated['question_count'] ?? 5;
        
        // Start a practice session
        $result = $this->agentService->executeAgent('skill_improvement_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'start_practice',
                'skill_id' => $id,
                'difficulty' => $difficulty,
                'question_count' => $questionCount
            ]
        ]);
        
        if (!$result['success']) {
            return $this->errorResponse(
                'Failed to start practice session',
                $result['details'] ?? null,
                500
            );
        }
        
        return $this->successResponse($result['data']);
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
    
    /**
     * Get due spaced repetition items
     * 
     * @return \Illuminate\Http\JsonResponse
     */
    public function getDueRepetitions()
    {
        $user = Auth::user();
        
        // Get due repetitions
        $result = $this->agentService->executeAgent('skill_improvement_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'get_due_repetitions'
            ]
        ]);
        
        if (!$result['success']) {
            return $this->errorResponse(
                'Failed to retrieve due repetitions',
                $result['details'] ?? null,
                500
            );
        }
        
        return $this->successResponse($result['data']);
    }
    
    /**
     * Complete a spaced repetition item
     * 
     * @param Request $request
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function completeRepetition(Request $request, $id)
    {
        $user = Auth::user();
        
        $validated = $request->validate([
            'performance_rating' => 'required|integer|min:0|max:5'
        ]);
        
        // Complete repetition
        $result = $this->agentService->executeAgent('skill_improvement_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'complete_repetition',
                'repetition_id' => $id,
                'performance_rating' => $validated['performance_rating']
            ]
        ]);
        
        if (!$result['success']) {
            return $this->errorResponse(
                'Failed to complete repetition',
                $result['details'] ?? null,
                500
            );
        }
        
        return $this->successResponse($result['data']);
    }
}