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

class LearningPlanController extends Controller
{
    public function getUserPlan($userId)
    {
        try {
            $user = User::findOrFail($userId);
            
            // Verify authorization
            $this->authorize('view', $user);
            
            $learningPlan = LearningPlan::where('user_id', $userId)
                ->with(['milestones' => function($query) {
                    $query->orderBy('sequence', 'asc');
                }])
                ->first();
            
            if (!$learningPlan) {
                // If no plan exists, create a default one
                $learningPlan = $this->createDefaultPlan($userId);
            }
            
            return response()->json($learningPlan);
        } catch (\Exception $e) {
            Log::error('Error retrieving learning plan: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to retrieve learning plan'], 500);
        }
    }
    
    /**
     * Create a default learning plan for a user
     *
     * @param int $userId
     * @return \App\Models\LearningPlan
     */
    private function createDefaultPlan($userId)
    {
        // This would normally call the LearningPlanAgent or service
        // For now, we'll create a simple default plan
        
        $learningPlan = new LearningPlan();
        $learningPlan->user_id = $userId;
        $learningPlan->title = 'Your Cybersecurity Learning Journey';
        $learningPlan->description = 'A personalized plan to improve your cybersecurity skills';
        $learningPlan->save();
        
        // Create default milestones
        $defaultMilestones = [
            [
                'title' => 'Complete Initial Assessment',
                'description' => 'Take the initial assessment quiz to establish your baseline',
                'sequence' => 1,
                'activity_type' => 'quiz',
                'activity_id' => 1, // ID of the baseline quiz
            ],
            [
                'title' => 'Review Your Strengths and Weaknesses',
                'description' => 'Analyze your assessment results',
                'sequence' => 2,
                'activity_type' => 'analytics',
                'activity_id' => null,
            ],
            // Add more default milestones as needed
        ];
        
        foreach ($defaultMilestones as $milestone) {
            $newMilestone = new Milestone();
            $newMilestone->learning_plan_id = $learningPlan->id;
            $newMilestone->title = $milestone['title'];
            $newMilestone->description = $milestone['description'];
            $newMilestone->sequence = $milestone['sequence'];
            $newMilestone->activity_type = $milestone['activity_type'];
            $newMilestone->activity_id = $milestone['activity_id'];
            $newMilestone->completed = false;
            $newMilestone->save();
        }
        
        return LearningPlan::where('id', $learningPlan->id)
            ->with(['milestones' => function($query) {
                $query->orderBy('sequence', 'asc');
            }])
            ->first();
    }
    
    /**
     * Update milestone completion status
     *
     * @param Request $request
     * @param int $userId
     * @param int $milestoneId
     * @return \Illuminate\Http\JsonResponse
     */
    public function updateMilestone(Request $request, $userId, $milestoneId)
    {
        try {
            $user = User::findOrFail($userId);
            
            // Verify authorization
            $this->authorize('update', $user);
            
            $milestone = Milestone::findOrFail($milestoneId);
            
            // Verify milestone belongs to user's plan
            $learningPlan = LearningPlan::where('user_id', $userId)->first();
            if (!$learningPlan || $milestone->learning_plan_id !== $learningPlan->id) {
                return response()->json(['error' => 'Unauthorized access to milestone'], 403);
            }
            
            // Update completion status
            $milestone->completed = $request->input('completed', false);
            $milestone->completed_at = $milestone->completed ? now() : null;
            $milestone->save();
            
            return response()->json($milestone);
        } catch (\Exception $e) {
            Log::error('Error updating milestone: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to update milestone'], 500);
        }
    }
}
