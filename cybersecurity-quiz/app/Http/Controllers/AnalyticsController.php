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
        
    // Get domain-specific scoring
    $domainScores = $this->getDomainScores($user->id);
    
    // Get benchmark comparisons
    $benchmarks = $this->getBenchmarkComparisons($user->id);
    
    // Get performance trends
    $trends = $this->getPerformanceTrends($user->id);
    
    return $this->successResponse([
        'skill_analytics' => $skillAnalytics,
        'recent_quizzes' => $recentQuizzes,
        'strengths' => $skillAnalytics->where('is_strength', true)->values(),
        'weaknesses' => $skillAnalytics->where('is_weakness', true)->values(),
        'domain_scores' => $domainScores,
        'benchmarks' => $benchmarks,
        'trends' => $trends,
        'total_quizzes' => UserQuizResult::where('user_id', $user->id)->count(),
        'avg_score' => UserQuizResult::where('user_id', $user->id)->avg('score') ?? 0,
        'skill_domains' => $this->getSkillDomains($user->id)
    ]);
}

/**
 * Get domain-specific scoring data
 *
 * @param int $userId
 * @return array
 */
private function getDomainScores($userId)
{
    // Call analytics agent to get domain scores
    $result = $this->agentService->executeAgent('analytics_agent', [
        'user_id' => $userId,
        'data' => [
            'action' => 'get_domain_scores'
        ]
    ]);
    
    if (!$result['success']) {
        return [];
    }
    
    return $result['data']['domain_scores'] ?? [];
}

/**
 * Get benchmark comparison data
 *
 * @param int $userId
 * @return array
 */
private function getBenchmarkComparisons($userId)
{
    // Call analytics agent to get benchmark comparisons
    $result = $this->agentService->executeAgent('analytics_agent', [
        'user_id' => $userId,
        'data' => [
            'action' => 'get_benchmark_comparisons'
        ]
    ]);
    
    if (!$result['success']) {
        return [];
    }
    
    return $result['data']['benchmarks'] ?? [];
}

/**
 * Get performance trends over time
 *
 * @param int $userId
 * @return array
 */
private function getPerformanceTrends($userId)
{
    // Get quiz results over time
    $results = UserQuizResult::where('user_id', $userId)
        ->orderBy('created_at')
        ->get()
        ->groupBy(function($date) {
            return Carbon::parse($date->created_at)->format('Y-m'); // Group by month
        });
    
    $trendData = [];
    
    foreach ($results as $month => $monthResults) {
        $trendData[] = [
            'month' => $month,
            'avg_score' => $monthResults->avg('score'),
            'quiz_count' => $monthResults->count()
        ];
    }
    
    return $trendData;
}

/**
 * Get skill domains with scores
 *
 * @param int $userId
 * @return array
 */
private function getSkillDomains($userId)
{
    // Call analytics agent to get skill domains
    $result = $this->agentService->executeAgent('analytics_agent', [
        'user_id' => $userId,
        'data' => [
            'action' => 'get_skill_domains'
        ]
    ]);
    
    if (!$result['success']) {
        return [];
    }
    
    return $result['data']['skill_domains'] ?? [];

 }
 public function getThreatAwarenessScoring()
{
    $user = Auth::user();
    
    // Get user's sector
    $sector = Sector::find($user->sector_id);
    
    if (!$sector) {
        return $this->errorResponse('User sector not found', null, 404);
    }
    
    // Call analytics agent to get threat awareness scoring
    $result = $this->agentService->executeAgent('analytics_agent', [
        'user_id' => $user->id,
        'data' => [
            'action' => 'get_threat_awareness',
            'sector_id' => $user->sector_id,
            'sector_name' => $sector->name
        ]
    ]);
    
    if (!$result['success']) {
        return $this->errorResponse(
            'Failed to retrieve threat awareness scoring',
            $result['details'] ?? null,
            500
        );
    }
    
    return $this->successResponse($result['data']);
}
}