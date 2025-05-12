<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use App\Models\Recommendation;
use App\Models\LearningResource;
use App\Services\AgentService;
use Illuminate\Support\Facades\Auth;
use Carbon\Carbon;

class RecommendationController extends Controller
{
    protected $agentService;

    public function __construct(AgentService $agentService)
    {
        $this->agentService = $agentService;
        $this->middleware('auth');
    }

    /**
     * Display user's recommendations
     */
    public function index()
    {
        $user = Auth::user();
        $recommendations = Recommendation::with('learningResource')
            ->where('user_id', $user->id)
            ->orderBy('relevance_score', 'desc')
            ->take(10)
            ->get();

        $skillGaps = $this->getUserSkillGaps($user->id);

        return view('recommendations.index', [
            'recommendations' => $recommendations,
            'skillGaps' => $skillGaps
        ]);
    }

    /**
     * Generate new recommendations
     */
    public function generate()
    {
        $user = Auth::user();
        $skillGaps = $this->getUserSkillGaps($user->id);

        // Only proceed if we have skill gaps to work with
        if (count($skillGaps) > 0) {
            // Call the recommendation agent
            $response = $this->agentService->executeAgent('recommendation', [
                'user_id' => $user->id,
                'skill_gaps' => $skillGaps
            ]);

            if ($response['status'] === 'success') {
                return redirect()->route('recommendations.index')
                    ->with('success', 'New recommendations generated successfully!');
            }
        }

        return redirect()->route('recommendations.index')
            ->with('error', 'Could not generate new recommendations at this time.');
    }

    /**
     * Mark recommendation as viewed
     */
    public function markViewed($id)
    {
        $recommendation = Recommendation::findOrFail($id);
        $this->authorize('update', $recommendation);

        $recommendation->is_viewed = true;
        $recommendation->save();

        return response()->json(['success' => true]);
    }

    /**
     * Mark recommendation as completed
     */
    public function markCompleted($id)
    {
        $recommendation = Recommendation::findOrFail($id);
        $this->authorize('update', $recommendation);

        $recommendation->is_completed = true;
        $recommendation->completed_at = Carbon::now();
        $recommendation->save();

        return redirect()->back()->with('success', 'Resource marked as completed!');
    }

    /**
     * Get user's skill gaps from analytics
     */
    private function getUserSkillGaps($userId)
    {
        // This would normally come from the AnalyticsAgent in Phase 3
        // For now, we'll retrieve the most recent quiz results and extract skill gaps
        $latestResult = \App\Models\UserQuizResult::where('user_id', $userId)
            ->orderBy('completed_at', 'desc')
            ->first();

        if ($latestResult && $latestResult->skill_gaps) {
            return json_decode($latestResult->skill_gaps, true);
        }

        // If no skill gaps found, return empty array
        return [];
    }
    public function getUserRecommendations($userId)
    {
        try {
            $user = User::findOrFail($userId);
            
            // Verify authorization
            $this->authorize('view', $user);
            
            // Get user's skill levels to determine recommendations
            $userSkills = UserSkill::where('user_id', $userId)
                ->join('skills', 'user_skills.skill_id', '=', 'skills.id')
                ->select(
                    'user_skills.*',
                    'skills.name as skill_name',
                    'skills.description as skill_description'
                )
                ->get();
            
            // Get existing recommendations
            $existingRecommendations = Recommendation::where('user_id', $userId)
                ->where('status', 'active')
                ->get();
            
            // If no recommendations or they're outdated, generate new ones
            if ($existingRecommendations->isEmpty() || 
                $existingRecommendations->first()->created_at->diffInDays(now()) > 7) {
                
                // Delete outdated recommendations
                Recommendation::where('user_id', $userId)
                    ->where('status', 'active')
                    ->update(['status' => 'archived']);
                
                // Generate new recommendations
                $recommendations = $this->generateRecommendations($user, $userSkills);
            } else {
                $recommendations = $existingRecommendations;
            }
            
            // Format recommendations for response
            $formattedRecommendations = [];
            foreach ($recommendations as $recommendation) {
                $resource = null;
                
                if ($recommendation->resource_type === 'learning_resource') {
                    $resource = LearningResource::find($recommendation->resource_id);
                } else if ($recommendation->resource_type === 'quiz') {
                    $resource = \App\Models\Quiz::find($recommendation->resource_id);
                }
                
                if ($resource) {
                    $formattedRecommendations[] = [
                        'id' => $recommendation->id,
                        'title' => $resource->title,
                        'description' => $resource->description,
                        'type' => $recommendation->resource_type,
                        'match_percentage' => $recommendation->match_percentage,
                        'resource_id' => $recommendation->resource_id,
                        'url' => $this->getResourceUrl($recommendation->resource_type, $recommendation->resource_id),
                        'skill_id' => $recommendation->skill_id
                    ];
                }
            }
            
            return response()->json([
                'user_id' => $userId,
                'resources' => $formattedRecommendations
            ]);
        } catch (\Exception $e) {
            Log::error('Error retrieving recommendations: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to retrieve recommendations'], 500);
        }
    }
    
    /**
     * Generate personalized recommendations
     *
     * @param User $user
     * @param Collection $userSkills
     * @return Collection
     */
    private function generateRecommendations($user, $userSkills)
    {
        // In a real implementation, this would call the RecommendationAgent
        // For now, we'll create sample recommendations
        
        $recommendations = collect();
        
        // Identify skills to improve (those with lowest proficiency)
        $skillsToImprove = $userSkills->sortBy('proficiency_level')->take(3);
        
        // For each skill to improve, find resources
        foreach ($skillsToImprove as $skill) {
            // Find learning resources for this skill
            // In a real implementation, this would query the database
            // For now, we'll create sample recommendations
            
            // Add a learning resource recommendation
            $recommendation = new Recommendation();
            $recommendation->user_id = $user->id;
            $recommendation->skill_id = $skill->skill_id;
            $recommendation->resource_type = 'learning_resource';
            $recommendation->resource_id = 1; // Sample resource ID
            $recommendation->match_percentage = 85;
            $recommendation->reason = 'Based on your skill gap in ' . $skill->skill_name;
            $recommendation->status = 'active';
            $recommendation->save();
            
            $recommendations->push($recommendation);
            
            // Add a quiz recommendation
            $recommendation = new Recommendation();
            $recommendation->user_id = $user->id;
            $recommendation->skill_id = $skill->skill_id;
            $recommendation->resource_type = 'quiz';
            $recommendation->resource_id = 1; // Sample quiz ID
            $recommendation->match_percentage = 90;
            $recommendation->reason = 'Practice quiz for ' . $skill->skill_name;
            $recommendation->status = 'active';
            $recommendation->save();
            
            $recommendations->push($recommendation);
        }
        
        return $recommendations;
    }
    
    /**
     * Get URL for a resource
     *
     * @param string $resourceType
     * @param int $resourceId
     * @return string
     */
    private function getResourceUrl($resourceType, $resourceId)
    {
        switch ($resourceType) {
            case 'learning_resource':
                $resource = LearningResource::find($resourceId);
                return $resource ? $resource->url : '#';
                
            case 'quiz':
                return '/quizzes/' . $resourceId;
                
            case 'course':
                return '/courses/' . $resourceId;
                
            default:
                return '#';
        }
    }
    
    /**
     * Record user interaction with a recommendation
     *
     * @param Request $request
     * @param int $userId
     * @param int $recommendationId
     * @return \Illuminate\Http\JsonResponse
     */
    public function recordInteraction(Request $request, $userId, $recommendationId)
    {
        try {
            $user = User::findOrFail($userId);
            
            // Verify authorization
            $this->authorize('update', $user);
            
            $recommendation = Recommendation::findOrFail($recommendationId);
            
            // Verify recommendation belongs to user
            if ($recommendation->user_id !== $user->id) {
                return response()->json(['error' => 'Unauthorized access to recommendation'], 403);
            }
            
            // Get interaction type
            $interactionType = $request->input('interaction_type', 'view');
            
            // Record interaction
            $interaction = new RecommendationInteraction();
            $interaction->recommendation_id = $recommendationId;
            $interaction->user_id = $userId;
            $interaction->interaction_type = $interactionType;
            $interaction->save();
            
            return response()->json([
                'message' => 'Interaction recorded successfully',
                'interaction_id' => $interaction->id
            ]);
        } catch (\Exception $e) {
            Log::error('Error recording recommendation interaction: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to record interaction'], 500);
        }
    }
}