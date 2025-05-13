<?php

namespace App\Http\Controllers;
use App\Http\Controllers\BaseApiController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Auth;
use App\Models\UserQuizResult;
use App\Models\Quiz;
use App\Models\User;
use App\Models\Skill;
use App\Models\Topic;
use App\Models\UserSkill;

class LearningPlanController extends BaseApiController
{
    protected $agentService;
    
    public function __construct(AgentService $agentService)
    {
        $this->agentService = $agentService;
    }
    
    /**
     * Get the user's learning plan
     * 
     * @return \Illuminate\Http\JsonResponse
     */
    public function index()
    {
        $user = Auth::user();
        $learningPlan = LearningPlan::with(['modules', 'modules.progress' => function ($query) use ($user) {
            $query->where('user_id', $user->id);
        }])
        ->where('user_id', $user->id)
        ->first();
            
        return $this->successResponse($learningPlan);
    }
    
    /**
     * Generate a new learning plan for the user
     * 
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function generate(Request $request)
    {
        $user = Auth::user();
        
        // Check if user already has a learning plan
        $existingPlan = LearningPlan::where('user_id', $user->id)->first();
        if ($existingPlan) {
            // Optionally archive existing plan
            $existingPlan->status = 'archived';
            $existingPlan->save();
        }
        
        // Call Python agent to generate learning plan
        $result = $this->agentService->executeAgent('learning_plan_agent', [
            'user_id' => $user->id,
            'data' => $request->all()
        ]);
        
        if (!$result['success']) {
            return $this->errorResponse(
                'Failed to generate learning plan',
                $result['details'] ?? null,
                500
            );
        }
        
        // The agent should have created the learning plan in the database
        // Refresh and return it
        $learningPlan = LearningPlan::with(['modules'])
            ->where('user_id', $user->id)
            ->where('status', 'active')
            ->latest()
            ->first();
            
        if (!$learningPlan) {
            return $this->errorResponse('Learning plan was not properly created', null, 500);
        }
            
        return $this->successResponse($learningPlan);
    }
    
    /**
     * Start a learning plan module
     * 
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function startModule($id)
    {
        $user = Auth::user();
        $module = LearningPlanModule::findOrFail($id);
        
        // Create or update progress record
        $progress = LearningPlanProgress::updateOrCreate(
            ['user_id' => $user->id, 'learning_plan_module_id' => $id],
            ['status' => 'in_progress', 'progress_percentage' => 0]
        );
        
        return $this->successResponse([
            'module' => $module,
            'content_reference_id' => $module->content_reference_id,
            'module_type' => $module->module_type
        ]);
    }
    
    /**
     * Update module progress
     * 
     * @param Request $request
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function updateProgress(Request $request, $id)
    {
        $user = Auth::user();
        $module = LearningPlanModule::findOrFail($id);
        
        $validated = $request->validate([
            'status' => 'required|in:not_started,in_progress,completed',
            'progress_percentage' => 'sometimes|numeric|min:0|max:100'
        ]);
        
        $progressData = [
            'status' => $validated['status']
        ];
        
        if (isset($validated['progress_percentage'])) {
            $progressData['progress_percentage'] = $validated['progress_percentage'];
        } else if ($validated['status'] === 'completed') {
            $progressData['progress_percentage'] = 100;
        }
        
        $progress = LearningPlanProgress::updateOrCreate(
            ['user_id' => $user->id, 'learning_plan_module_id' => $id],
            $progressData
        );
        
        // Update overall learning plan progress
        $this->updateLearningPlanProgress($module->learning_plan_id);
        
        return $this->successResponse($progress);
    }
    
    /**
     * Update the overall learning plan progress
     * 
     * @param int $learningPlanId
     * @return \App\Models\LearningPlan
     */
    private function updateLearningPlanProgress($learningPlanId)
    {
        $learningPlan = LearningPlan::findOrFail($learningPlanId);
        $modules = LearningPlanModule::where('learning_plan_id', $learningPlanId)->get();
        $user = Auth::user();
        
        $totalModules = $modules->count();
        $totalProgress = 0;
        
        foreach ($modules as $module) {
            $progress = LearningPlanProgress::where('user_id', $user->id)
                ->where('learning_plan_module_id', $module->id)
                ->first();
            
            if ($progress) {
                $totalProgress += $progress->progress_percentage;
            }
        }
        
        $overallProgress = $totalModules > 0 ? round($totalProgress / $totalModules) : 0;
        
        $learningPlan->overall_progress = $overallProgress;
        $learningPlan->save();
        
        return $learningPlan;
    }
}
