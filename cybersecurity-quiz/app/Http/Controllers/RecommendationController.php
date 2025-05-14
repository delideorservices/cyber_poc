<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\AgentService;
use App\Models\ResourceRecommendation;
use App\Models\Resource; 
use Illuminate\Support\Facades\Auth;
use App\Http\Controllers\BaseApiController;

class RecommendationController extends BaseApiController
{
    protected $agentService;
    
    public function __construct(AgentService $agentService)
    {
        $this->agentService = $agentService;
    }
    
    /**
     * Get personalized recommendations for the user
     * 
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
 public function getRecommendations(Request $request)
{
    $user = Auth::user();
    
    // Check for filtering and paging
    $type = $request->input('type');
    $limit = $request->input('limit', 10);
    $learningStyle = $request->input('learning_style');
    $skillFocus = $request->input('skill_focus');
    $difficulty = $request->input('difficulty');
    
    // Get user's learning style preference or use default
    if (!$learningStyle) {
        $learningStyle = $user->learning_style_preference ?? 'visual';
    }
    
    // First check existing recommendations
    $query = ResourceRecommendation::with('resource')
        ->where('user_id', $user->id)
        ->where('status', 'new');
        
    if ($type) {
        $query->whereHas('resource', function ($q) use ($type) {
            $q->where('resource_type', $type);
        });
    }
    
    // Add difficulty filter if specified
    if ($difficulty) {
        $query->whereHas('resource', function ($q) use ($difficulty) {
            $q->where('difficulty_level', $difficulty);
        });
    }
    
    // Add skill focus filter if specified
    if ($skillFocus) {
        $query->whereHas('resource', function ($q) use ($skillFocus) {
            $q->where('primary_skill_id', $skillFocus)
              ->orWhereJsonContains('related_skills', $skillFocus);
        });
    }
    
    $recommendations = $query->latest()->take($limit)->get();
    
    // If no recommendations exist or fewer than requested, generate new ones
    if ($recommendations->count() < $limit) {
        // Get user's analytics to inform recommendations
        $skillAnalytics = SkillAnalytic::where('user_id', $user->id)->get();
        
        // Get previous completed resources to avoid duplication
        $completedResourceIds = ResourceRecommendation::where('user_id', $user->id)
            ->where('status', 'completed')
            ->pluck('resource_id')
            ->toArray();
        
        // Get user quiz history
        $quizResults = UserQuizResult::where('user_id', $user->id)
            ->with('quiz')
            ->latest()
            ->take(10)
            ->get();
        
        $result = $this->agentService->executeAgent('recommendation_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'generate_recommendations',
                'count' => $limit - $recommendations->count(),
                'type' => $type,
                'learning_style' => $learningStyle,
                'skill_focus' => $skillFocus,
                'difficulty' => $difficulty,
                'user_context' => [
                    'sector_id' => $user->sector_id,
                    'role_id' => $user->role_id,
                    'years_experience' => $user->years_experience,
                    'learning_goal' => $user->learning_goal
                ],
                'skill_analytics' => $skillAnalytics->toArray(),
                'completed_resources' => $completedResourceIds,
                'quiz_history' => $quizResults->toArray()
            ]
        ]);
        
        if (!$result['success']) {
            // Continue with existing recommendations even if new generation fails
            // but log the error
            \Log::error('Failed to generate new recommendations', [
                'user_id' => $user->id,
                'error' => $result['error'] ?? 'Unknown error'
            ]);
        } else {
            // Refresh recommendations after generation
            $query = ResourceRecommendation::with('resource')
                ->where('user_id', $user->id)
                ->where('status', 'new');
                
            if ($type) {
                $query->whereHas('resource', function ($q) use ($type) {
                    $q->where('resource_type', $type);
                });
            }
            
            if ($difficulty) {
                $query->whereHas('resource', function ($q) use ($difficulty) {
                    $q->where('difficulty_level', $difficulty);
                });
            }
            
            if ($skillFocus) {
                $query->whereHas('resource', function ($q) use ($skillFocus) {
                    $q->where('primary_skill_id', $skillFocus)
                      ->orWhereJsonContains('related_skills', $skillFocus);
                });
            }
            
            $recommendations = $query->latest()->take($limit)->get();
        }
    }
    
    // Get resource types for filtering
    $resourceTypes = Resource::distinct('resource_type')->pluck('resource_type');
    
    // Get available learning styles
    $learningStyles = [
        'visual' => 'Visual',
        'auditory' => 'Auditory',
        'reading' => 'Reading/Writing',
        'kinesthetic' => 'Kinesthetic/Hands-on'
    ];
    
    // Get skill options for filtering
    $skills = Skill::orderBy('name')->get(['id', 'name']);
    
    // Get difficulty levels
    $difficultyLevels = [
        1 => 'Beginner',
        2 => 'Easy',
        3 => 'Intermediate',
        4 => 'Advanced',
        5 => 'Expert'
    ];
    
    return $this->successResponse([
        'recommendations' => $recommendations,
        'resource_types' => $resourceTypes,
        'learning_styles' => $learningStyles,
        'user_learning_style' => $learningStyle,
        'skills' => $skills,
        'difficulty_levels' => $difficultyLevels,
        'filter_options' => [
            'current_type' => $type,
            'current_skill_focus' => $skillFocus,
            'current_difficulty' => $difficulty
        ]
    ]);
}
    
    /**
     * Get saved recommendations
     * 
     * @return \Illuminate\Http\JsonResponse
     */
    public function getSavedRecommendations()
    {
        $user = Auth::user();
        
        $savedRecommendations = ResourceRecommendation::with('resource')
            ->where('user_id', $user->id)
            ->where('status', 'saved')
            ->latest()
            ->get();
            
        return $this->successResponse($savedRecommendations);
    }
    
    /**
     * Mark a recommendation as viewed
     * 
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function viewRecommendation($id)
    {
        $user = Auth::user();
        
        $recommendation = ResourceRecommendation::where('user_id', $user->id)
            ->where('id', $id)
            ->firstOrFail();
            
        $recommendation->status = 'viewed';
        $recommendation->viewed_at = now();
        $recommendation->save();
        
        return $this->successResponse($recommendation);
    }
    
    /**
     * Mark a recommendation as completed
     * 
     * @param Request $request
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function completeRecommendation(Request $request, $id)
    {
        $user = Auth::user();
        
        $validated = $request->validate([
            'rating' => 'sometimes|integer|min:1|max:5',
            'feedback' => 'sometimes|string|max:500'
        ]);
        
        $recommendation = ResourceRecommendation::where('user_id', $user->id)
            ->where('id', $id)
            ->firstOrFail();
            
        $recommendation->status = 'completed';
        $recommendation->completed_at = now();
        
        if (isset($validated['rating'])) {
            $recommendation->user_rating = $validated['rating'];
        }
        
        if (isset($validated['feedback'])) {
            $recommendation->user_feedback = $validated['feedback'];
        }
        
        $recommendation->save();
        
        // If we have feedback, send it to the recommendation agent for improvement
        if (isset($validated['rating']) || isset($validated['feedback'])) {
            $this->agentService->executeAgent('recommendation_agent', [
                'user_id' => $user->id,
                'data' => [
                    'action' => 'process_feedback',
                    'recommendation_id' => $id,
                    'rating' => $validated['rating'] ?? null,
                    'feedback' => $validated['feedback'] ?? null
                ]
            ]);
        }
        
        return $this->successResponse($recommendation);
    }
    
    /**
     * Save a recommendation for later
     * 
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function saveRecommendation($id)
    {
        $user = Auth::user();
        
        $recommendation = ResourceRecommendation::where('user_id', $user->id)
            ->where('id', $id)
            ->firstOrFail();
            
        $recommendation->status = 'saved';
        $recommendation->save();
        
        return $this->successResponse($recommendation);
    }
    
    /**
     * Remove a saved recommendation
     * 
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function removeSavedRecommendation($id)
    {
        $user = Auth::user();
        
        $recommendation = ResourceRecommendation::where('user_id', $user->id)
            ->where('id', $id)
            ->where('status', 'saved')
            ->firstOrFail();
            
        $recommendation->status = 'dismissed';
        $recommendation->save();
        
        return $this->successResponse(null, 'Recommendation removed from saved items');
    }
    public function processFeedback(Request $request)
{
    $user = Auth::user();
    
    $validated = $request->validate([
        'recommendation_id' => 'required|exists:resource_recommendations,id',
        'relevance_rating' => 'required|integer|min:1|max:5',
        'content_quality_rating' => 'required|integer|min:1|max:5',
        'learning_style_fit' => 'required|integer|min:1|max:5',
        'difficulty_appropriateness' => 'required|integer|min:1|max:5',
        'specific_feedback' => 'sometimes|string|max:1000'
    ]);
    
    // Retrieve the recommendation
    $recommendation = ResourceRecommendation::where('id', $validated['recommendation_id'])
                                           ->where('user_id', $user->id)
                                           ->firstOrFail();
    
    // Store the detailed feedback
    $recommendation->feedback_data = [
        'relevance_rating' => $validated['relevance_rating'],
        'content_quality_rating' => $validated['content_quality_rating'],
        'learning_style_fit' => $validated['learning_style_fit'],
        'difficulty_appropriateness' => $validated['difficulty_appropriateness'],
        'specific_feedback' => $validated['specific_feedback'] ?? null,
        'feedback_date' => now()->toDateTimeString()
    ];
    
    // Calculate overall rating from components
    $recommendation->user_rating = round((
        $validated['relevance_rating'] + 
        $validated['content_quality_rating'] + 
        $validated['learning_style_fit'] + 
        $validated['difficulty_appropriateness']
    ) / 4);
    
    $recommendation->user_feedback = $validated['specific_feedback'] ?? null;
    $recommendation->save();
    
    // Send feedback to recommendation agent for model improvement
    $this->agentService->executeAgent('recommendation_agent', [
        'user_id' => $user->id,
        'data' => [
            'action' => 'process_feedback',
            'recommendation_id' => $recommendation->id,
            'resource_id' => $recommendation->resource_id,
            'resource_type' => $recommendation->resource->resource_type,
            'feedback' => $recommendation->feedback_data
        ]
    ]);
    
    return $this->successResponse([
        'message' => 'Feedback processed successfully',
        'recommendation' => $recommendation
    ]);
}
}