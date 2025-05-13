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
        
        // First check existing recommendations
        $query = ResourceRecommendation::with('resource')
            ->where('user_id', $user->id)
            ->where('status', 'new');
            
        if ($type) {
            $query->whereHas('resource', function ($q) use ($type) {
                $q->where('resource_type', $type);
            });
        }
        
        $recommendations = $query->latest()->take($limit)->get();
        
        // If no recommendations exist or fewer than requested, generate new ones
        if ($recommendations->count() < $limit) {
            $result = $this->agentService->executeAgent('recommendation_agent', [
                'user_id' => $user->id,
                'data' => [
                    'action' => 'generate_recommendations',
                    'count' => $limit - $recommendations->count(),
                    'type' => $type
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
                
                $recommendations = $query->latest()->take($limit)->get();
            }
        }
        
        // Get resource types for filtering
        $resourceTypes = Resource::distinct('resource_type')->pluck('resource_type');
        
        return $this->successResponse([
            'recommendations' => $recommendations,
            'resource_types' => $resourceTypes
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
}