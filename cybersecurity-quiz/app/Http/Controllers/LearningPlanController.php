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
    
    // Validate the request
    $validated = $request->validate([
        'focus_areas' => 'sometimes|array',
        'certification_goals' => 'sometimes|array',
        'difficulty_preference' => 'sometimes|integer|min:1|max:5',
        'time_commitment' => 'sometimes|integer|min:1|max:40', // hours per week
        'target_completion_date' => 'sometimes|date|after:now'
    ]);
    
    // Check if user already has a learning plan
    $existingPlan = LearningPlan::where('user_id', $user->id)
                                ->where('status', 'active')
                                ->first();
    if ($existingPlan) {
        // Optionally archive existing plan
        $existingPlan->status = 'archived';
        $existingPlan->save();
    }
    
    // Get user's skill analytics for input to the learning plan
    $skillAnalytics = SkillAnalytic::where('user_id', $user->id)->get();
    
    // If no analytics exist, generate them first
    if ($skillAnalytics->isEmpty()) {
        $analyticsResult = $this->agentService->executeAgent('analytics_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'generate_analytics'
            ]
        ]);
        
        if (!$analyticsResult['success']) {
            return $this->errorResponse(
                'Failed to generate prerequisite analytics',
                $analyticsResult['details'] ?? null,
                500
            );
        }
        
        // Refresh skill analytics
        $skillAnalytics = SkillAnalytic::where('user_id', $user->id)->get();
    }
    
    // Get user certifications for context
    $userCertifications = $user->certifications()->get();
    
    // Get recent quiz results
    $recentResults = UserQuizResult::where('user_id', $user->id)
                                  ->with('quiz')
                                  ->latest()
                                  ->take(5)
                                  ->get();
    
    // Call Python agent to generate learning plan
    $result = $this->agentService->executeAgent('learning_plan_agent', [
        'user_id' => $user->id,
        'data' => [
            'action' => 'generate_plan',
            'user_profile' => [
                'name' => $user->name,
                'email' => $user->email,
                'sector_id' => $user->sector_id,
                'role_id' => $user->role_id,
                'years_experience' => $user->years_experience,
                'learning_goal' => $user->learning_goal,
                'skills' => $user->skills()->get()->map(function($skill) {
                    return [
                        'id' => $skill->id,
                        'name' => $skill->name,
                        'proficiency' => $skill->pivot->proficiency_level
                    ];
                })->toArray(),
                'certifications' => $userCertifications->map(function($cert) {
                    return [
                        'id' => $cert->id,
                        'name' => $cert->name,
                        'obtained_date' => $cert->pivot->obtained_date,
                        'expiry_date' => $cert->pivot->expiry_date
                    ];
                })->toArray()
            ],
            'skill_analytics' => $skillAnalytics->toArray(),
            'recent_results' => $recentResults->toArray(),
            'preferences' => [
                'focus_areas' => $validated['focus_areas'] ?? [],
                'certification_goals' => $validated['certification_goals'] ?? [],
                'difficulty_preference' => $validated['difficulty_preference'] ?? 3,
                'time_commitment' => $validated['time_commitment'] ?? 10,
                'target_completion_date' => $validated['target_completion_date'] ?? null
            ]
        ]
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
    
public function mapToCertification(Request $request, $id)
{
    $user = Auth::user();
    
    $validated = $request->validate([
        'certification_id' => 'required|exists:certifications,id'
    ]);
    
    $learningPlan = LearningPlan::where('user_id', $user->id)
                              ->where('id', $id)
                              ->first();
    
    if (!$learningPlan) {
        return $this->errorResponse('Learning plan not found', null, 404);
    }
    
    // Get the certification
    $certification = Certification::find($validated['certification_id']);
    
    // Call the learning plan agent to map modules to certification requirements
    $result = $this->agentService->executeAgent('learning_plan_agent', [
        'user_id' => $user->id,
        'data' => [
            'action' => 'map_to_certification',
            'learning_plan_id' => $learningPlan->id,
            'certification_id' => $certification->id,
            'certification_name' => $certification->name,
            'certification_details' => $certification->requirements
        ]
    ]);
    
    if (!$result['success']) {
        return $this->errorResponse(
            'Failed to map learning plan to certification',
            $result['details'] ?? null,
            500
        );
    }
    
    // Refresh the learning plan with updated modules
    $learningPlan = LearningPlan::with(['modules'])
        ->where('id', $id)
        ->first();
    
    return $this->successResponse([
        'learning_plan' => $learningPlan,
        'certification' => $certification,
        'mapping_details' => $result['data']['mapping_details'] ?? []
    ]);
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
