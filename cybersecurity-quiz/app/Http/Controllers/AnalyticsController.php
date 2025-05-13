<?php
namespace App\Http\Controllers;
use App\Http\Controllers\BaseApiController;
use Illuminate\Http\Request;
use App\Services\AgentService;
use App\Models\SkillAnalytic;
use App\Models\UserQuizResult;
use Illuminate\Support\Facades\Auth;

class AnalyticsController extends BaseApiController
{
    protected $agentService;
    
    public function __construct(AgentService $agentService)
    {
        $this->agentService = $agentService;
    }
    
    /**
     * Get user analytics dashboard data
     * 
     * @return \Illuminate\Http\JsonResponse
     */
    public function getUserAnalytics()
    {
        $user = Auth::user();
        
        // Get the user's skill analytics
        $skillAnalytics = SkillAnalytic::where('user_id', $user->id)->get();
        
        // If no analytics exist, generate them using the analytics agent
        if ($skillAnalytics->isEmpty()) {
            $result = $this->agentService->executeAgent('analytics_agent', [
                'user_id' => $user->id,
                'data' => [
                    'action' => 'generate_analytics'
                ]
            ]);
            
            if (!$result['success']) {
                return $this->errorResponse(
                    'Failed to generate user analytics',
                    $result['details'] ?? null,
                    500
                );
            }
            
            // Refresh skill analytics after generation
            $skillAnalytics = SkillAnalytic::where('user_id', $user->id)->get();
        }
        
        // Get recent quiz results
        $recentQuizzes = UserQuizResult::with('quiz', 'quiz.topic')
            ->where('user_id', $user->id)
            ->latest()
            ->take(5)
            ->get();
            
        return $this->successResponse([
            'skill_analytics' => $skillAnalytics,
            'recent_quizzes' => $recentQuizzes,
            'strengths' => $skillAnalytics->where('is_strength', true)->values(),
            'weaknesses' => $skillAnalytics->where('is_weakness', true)->values(),
        ]);
    }
    
    /**
     * Get detailed analytics for a specific skill
     * 
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function getSkillAnalytics($id)
    {
        $user = Auth::user();
        
        // Get detailed analytics for the specific skill
        $result = $this->agentService->executeAgent('analytics_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'get_skill_analytics',
                'skill_id' => $id
            ]
        ]);
        
        if (!$result['success']) {
            return $this->errorResponse(
                'Failed to retrieve skill analytics',
                $result['details'] ?? null,
                500
            );
        }
        
        return $this->successResponse($result['data']);
    }
    
    /**
     * Get peer comparison data
     * 
     * @return \Illuminate\Http\JsonResponse
     */
    public function getPeerComparison()
    {
        $user = Auth::user();
        
        // Get peer comparison data
        $result = $this->agentService->executeAgent('analytics_agent', [
            'user_id' => $user->id,
            'data' => [
                'action' => 'get_peer_comparison'
            ]
        ]);
        
        if (!$result['success']) {
            return $this->errorResponse(
                'Failed to retrieve peer comparison data',
                $result['details'] ?? null,
                500
            );
        }
        
        return $this->successResponse($result['data']);
    }
    
    /**
     * Export user analytics as CSV
     * 
     * @return \Symfony\Component\HttpFoundation\BinaryFileResponse
     */
    public function exportAnalytics()
    {
        $user = Auth::user();
        
        // Get user skill analytics
        $skillAnalytics = SkillAnalytic::where('user_id', $user->id)->get();
        
        // Generate CSV file
        $fileName = 'skill_analytics_' . $user->id . '_' . date('Y-m-d') . '.csv';
        $headers = [
            "Content-type" => "text/csv",
            "Content-Disposition" => "attachment; filename=$fileName",
            "Pragma" => "no-cache",
            "Cache-Control" => "must-revalidate, post-check=0, pre-check=0",
            "Expires" => "0"
        ];
        
        $columns = ['Skill', 'Proficiency Score', 'Strength Level', 'Is Strength', 'Is Weakness', 'Benchmark Percentile'];
        
        $callback = function() use($skillAnalytics, $columns) {
            $file = fopen('php://output', 'w');
            fputcsv($file, $columns);
            
            foreach ($skillAnalytics as $analytics) {
                $row = [
                    $analytics->skill->name ?? "Skill #$analytics->skill_id",
                    $analytics->proficiency_score,
                    $analytics->strength_level,
                    $analytics->is_strength ? 'Yes' : 'No',
                    $analytics->is_weakness ? 'Yes' : 'No',
                    $analytics->benchmark_percentile
                ];
                
                fputcsv($file, $row);
            }
            
            fclose($file);
        };
        
        return response()->stream($callback, 200, $headers);
    }
}