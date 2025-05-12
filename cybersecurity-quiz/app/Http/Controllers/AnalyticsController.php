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


class AnalyticsController extends Controller
{
    /**
     * Show the analytics dashboard for the authenticated user
     */
    public function dashboard()
    {
        $user = Auth::user();
        
        // Get recent quiz results
        $recentQuizzes = UserQuizResult::where('user_id', $user->id)
            ->with(['quiz', 'quiz.topic'])
            ->orderBy('created_at', 'desc')
            ->take(5)
            ->get();
            
        // Get overall stats
        $stats = $this->getUserStats($user->id);
        
        return view('analytics.dashboard', [
            'user' => $user,
            'recentQuizzes' => $recentQuizzes,
            'stats' => $stats
        ]);
    }
    
    /**
     * Show detailed analytics for a specific quiz
     */
    public function quizAnalytics($quizResultId)
    {
        $quizResult = UserQuizResult::findOrFail($quizResultId);
        
        // Check authorization
        $this->authorize('view', $quizResult);
        
        // Call the AI analytics agent to get enhanced analysis
        $analysisData = $this->getEnhancedAnalysis($quizResult->user_id, $quizResult->quiz_id);
        
        return view('analytics.quiz', [
            'quizResult' => $quizResult,
            'analysis' => $analysisData,
        ]);
    }
    
    /**
     * Show skill proficiency analysis across all quizzes
     */
    public function skillAnalytics()
    {
        $user = Auth::user();
        
        // Get skill performance data
        $skillPerformance = $this->getSkillPerformance($user->id);
        
        // Get peer comparison data
        $peerComparison = $this->getPeerComparison($user->id);
        
        return view('analytics.skills', [
            'user' => $user,
            'skillPerformance' => $skillPerformance,
            'peerComparison' => $peerComparison
        ]);
    }
    
    /**
     * API endpoint to get enhanced quiz analysis
     */
    public function getEnhancedAnalysis($userId, $quizId)
    {
        // Call the AI backend to run the enhanced analytics agent
        $response = Http::post(config('services.ai_backend.url') . '/analytics/enhanced', [
            'user_id' => $userId,
            'quiz_id' => $quizId,
        ]);
        
        if ($response->successful()) {
            return $response->json();
        }
        
        // Fallback to basic analysis if AI backend fails
        return $this->getFallbackAnalysis($userId, $quizId);
    }
    
    /**
     * Get user's overall stats
     */
    private function getUserStats($userId)
    {
        $stats = [
            'quizzes_taken' => UserQuizResult::where('user_id', $userId)->count(),
            'avg_score' => UserQuizResult::where('user_id', $userId)->avg('percentage_score'),
            'total_points' => UserQuizResult::where('user_id', $userId)->sum('total_points'),
        ];
        
        // Get skill coverage
        $skillsCovered = \DB::table('user_responses as ur')
            ->join('questions as q', 'ur.question_id', '=', 'q.id')
            ->join('skills as s', 'q.skill_id', '=', 's.id')
            ->where('ur.user_id', $userId)
            ->distinct('s.id')
            ->count('s.id');
            
        $totalSkills = Skill::count();
        $stats['skill_coverage'] = [
            'covered' => $skillsCovered,
            'total' => $totalSkills,
            'percentage' => $totalSkills > 0 ? ($skillsCovered / $totalSkills) * 100 : 0
        ];
        
        return $stats;
    }
    
    /**
     * Get skill performance data across all quizzes
     */
    private function getSkillPerformance($userId)
    {
        // Query user responses grouped by skill
        $skillPerformance = \DB::table('user_responses as ur')
            ->join('questions as q', 'ur.question_id', '=', 'q.id')
            ->join('skills as s', 'q.skill_id', '=', 's.id')
            ->where('ur.user_id', $userId)
            ->select(
                's.id as skill_id',
                's.name as skill_name',
                \DB::raw('COUNT(DISTINCT ur.question_id) as total_questions'),
                \DB::raw('SUM(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) as correct_answers'),
                \DB::raw('AVG(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) * 100 as score_percentage')
            )
            ->groupBy('s.id', 's.name')
            ->get();
            
        return $skillPerformance;
    }
    
    /**
     * Get peer comparison data
     */
    private function getPeerComparison($userId)
    {
        $user = User::find($userId);
        
        // Find similar users (same sector and role)
        $similarUserIds = User::where('sector_id', $user->sector_id)
            ->where('role_id', $user->role_id)
            ->where('id', '!=', $userId)
            ->pluck('id');
            
        if ($similarUserIds->isEmpty()) {
            return [
                'status' => 'insufficient_data',
                'message' => 'Not enough peer data available for comparison'
            ];
        }
        
        // Get peer performance by skill
        $peerPerformance = \DB::table('user_responses as ur')
            ->join('questions as q', 'ur.question_id', '=', 'q.id')
            ->join('skills as s', 'q.skill_id', '=', 's.id')
            ->whereIn('ur.user_id', $similarUserIds)
            ->select(
                's.id as skill_id',
                's.name as skill_name',
                \DB::raw('AVG(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) * 100 as avg_score'),
                \DB::raw('COUNT(DISTINCT ur.user_id) as user_count')
            )
            ->groupBy('s.id', 's.name')
            ->get();
            
        // Format the comparison
        $skillComparison = [];
        $userPerformance = $this->getSkillPerformance($userId);
        
        foreach ($userPerformance as $userSkill) {
            $peerSkill = $peerPerformance->firstWhere('skill_id', $userSkill->skill_id);
            
            if ($peerSkill) {
                $differential = $userSkill->score_percentage - $peerSkill->avg_score;
                $percentile = $this->calculatePercentile($userSkill->score_percentage, $peerSkill->avg_score);
                
                $skillComparison[$userSkill->skill_id] = [
                    'skill_id' => $userSkill->skill_id,
                    'skill_name' => $userSkill->skill_name,
                    'user_score' => $userSkill->score_percentage,
                    'peer_average' => $peerSkill->avg_score,
                    'differential' => $differential,
                    'percentile' => $percentile
                ];
            }
        }
        
        return [
            'skill_comparison' => $skillComparison,
            'peer_count' => $similarUserIds->count(),
            'status' => 'success'
        ];
    }
    
    /**
     * Calculate approximate percentile
     */
    private function calculatePercentile($score, $average, $stdDev = 15)
    {
        $zScore = ($score - $average) / $stdDev;
        $percentile = (self::normalCDF($zScore) * 100);
        return round($percentile, 1);
    }
    
    /**
     * Normal cumulative distribution function
     */
    private static function normalCDF($x)
    {
        $b1 =  0.319381530;
        $b2 = -0.356563782;
        $b3 =  1.781477937;
        $b4 = -1.821255978;
        $b5 =  1.330274429;
        $p  =  0.2316419;
        $c  =  0.39894228;

        if ($x >= 0.0) {
            $t = 1.0 / (1.0 + $p * $x);
            return (1.0 - $c * exp(-$x * $x / 2.0) * $t *
                ($t * ($t * ($t * ($t * $b5 + $b4) + $b3) + $b2) + $b1));
        }
        
        $t = 1.0 / (1.0 - $p * $x);
        return ($c * exp(-$x * $x / 2.0) * $t *
            ($t * ($t * ($t * ($t * $b5 + $b4) + $b3) + $b2) + $b1));
    }
    
    /**
     * Fallback analysis if AI backend is unavailable
     */
    private function getFallbackAnalysis($userId, $quizId)
    {
        $quizResult = UserQuizResult::where('user_id', $userId)
            ->where('quiz_id', $quizId)
            ->firstOrFail();
            
        $responses = \DB::table('user_responses as ur')
            ->join('questions as q', 'ur.question_id', '=', 'q.id')
            ->join('chapters as ch', 'q.chapter_id', '=', 'ch.id')
            ->where('ur.user_id', $userId)
            ->where('ch.quiz_id', $quizId)
            ->select('ur.*', 'q.skill_id', 'ch.title as chapter_title')
            ->get();
            
        // Build basic analysis
        $strengths = [];
        $weaknesses = [];
        $skillPerformance = [];
        
        // Group responses by skill
        $skillResponses = $responses->groupBy('skill_id');
        
        foreach ($skillResponses as $skillId => $skillResp) {
            if (!$skillId) continue;
            
            $skill = Skill::find($skillId);
            $correct = $skillResp->where('is_correct', true)->count();
            $total = $skillResp->count();
            $score = ($total > 0) ? ($correct / $total) * 100 : 0;
            
            $skillPerformance[$skillId] = [
                'skill_id' => $skillId,
                'skill_name' => $skill->name,
                'score' => $score,
                'correct' => $correct,
                'total' => $total
            ];
            
            if ($score >= 80) {
                $strengths[] = [
                    'skill_id' => $skillId,
                    'skill_name' => $skill->name,
                    'score' => $score
                ];
            } elseif ($score <= 50) {
                $weaknesses[] = [
                    'skill_id' => $skillId,
                    'skill_name' => $skill->name,
                    'score' => $score
                ];
            }
        }
        
        return [
            'user_id' => $userId,
            'quiz_id' => $quizId,
            'overall_score' => $quizResult->percentage_score,
            'strength_weakness' => [
                'strengths' => $strengths,
                'weaknesses' => $weaknesses
            ],
            'skill_performance' => $skillPerformance,
            'status' => 'fallback'
        ];
    }
    public function getUserAnalytics($userId)
    {
        try {
            $user = User::findOrFail($userId);
            
            // Verify authorization
            $this->authorize('view', $user);
            
            // Get user skills with scores
            $userSkills = UserSkill::where('user_id', $userId)
                ->join('skills', 'user_skills.skill_id', '=', 'skills.id')
                ->select(
                    'user_skills.*',
                    'skills.name as skill_name',
                    'skills.description as skill_description'
                )
                ->get();
            
            // Get sector benchmarks if user has a sector
            $sectorBenchmarks = [];
            if ($user->sector_id) {
                $sectorBenchmarks = $this->getSectorBenchmarks($user->sector_id);
            }
            
            // Identify strengths (high-scoring skills)
            $strengths = $userSkills->filter(function($skill) use ($sectorBenchmarks) {
                $benchmarkScore = $sectorBenchmarks[$skill->skill_id] ?? 70; // Default benchmark
                return $skill->proficiency_level >= $benchmarkScore;
            })->values();
            
            // Identify skill gaps (low-scoring skills)
            $skillGaps = $userSkills->filter(function($skill) use ($sectorBenchmarks) {
                $benchmarkScore = $sectorBenchmarks[$skill->skill_id] ?? 70; // Default benchmark
                return $skill->proficiency_level < $benchmarkScore;
            })->values();
            
            // Get performance trend data
            $performanceTrend = $this->getPerformanceTrend($userId);
            
            // Compile analytics data
            $analyticsData = [
                'user_name' => $user->name,
                'all_skills' => $userSkills,
                'strengths' => $strengths,
                'skill_gaps' => $skillGaps,
                'sector_comparison' => [
                    'sector_name' => $user->sector ? $user->sector->name : 'General',
                    'benchmarks' => $sectorBenchmarks
                ],
                'performance_trend' => $performanceTrend
            ];
            
            return response()->json($analyticsData);
        } catch (\Exception $e) {
            Log::error('Error retrieving analytics data: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to retrieve analytics data'], 500);
        }
    }
    
    /**
     * Get benchmark scores for skills in a specific sector
     *
     * @param int $sectorId
     * @return array
     */
    private function getSectorBenchmarks($sectorId)
    {
        // This would typically be calculated from aggregate user data
        // For now, we'll return some sample benchmarks
        
        // Get all skills
        $skills = Skill::all();
        
        // Create benchmark mapping
        $benchmarks = [];
        foreach ($skills as $skill) {
            // In a real implementation, this would query for actual sector averages
            $benchmarks[$skill->id] = rand(65, 85); // Sample benchmark scores
        }
        
        return $benchmarks;
    }
    
    /**
     * Get performance trend data over time
     *
     * @param int $userId
     * @return array
     */
    private function getPerformanceTrend($userId)
    {
        // Get user quiz results ordered by date
        $quizResults = UserQuizResult::where('user_id', $userId)
            ->orderBy('completed_at', 'asc')
            ->get();
        
        // Format trend data
        $trendData = [];
        foreach ($quizResults as $result) {
            $trendData[] = [
                'date' => $result->completed_at->format('Y-m-d'),
                'score' => $result->percentage_score,
                'quiz_id' => $result->quiz_id,
                'quiz_title' => $result->quiz ? $result->quiz->title : 'Unknown Quiz'
            ];
        }
        
        return $trendData;
    }
    
    /**
     * Get skill improvement activities
     *
     * @param int $userId
     * @param int $skillId
     * @return \Illuminate\Http\JsonResponse
     */
    public function getSkillImprovementActivities($userId, $skillId)
    {
        try {
            $user = User::findOrFail($userId);
            
            // Verify authorization
            $this->authorize('view', $user);
            
            $skill = Skill::findOrFail($skillId);
            
            // Get user's current skill level
            $userSkill = UserSkill::where('user_id', $userId)
                ->where('skill_id', $skillId)
                ->first();
            
            $currentLevel = $userSkill ? $userSkill->proficiency_level : 0;
            
            // Generate practice options at different difficulty levels
            $practiceOptions = [];
            
            // Easier practice (if not already at beginner level)
            if ($currentLevel > 20) {
                $practiceOptions[] = [
                    'title' => 'Basic Practice: ' . $skill->name . ' Fundamentals',
                    'description' => 'Reinforce your understanding of basic concepts',
                    'difficulty_level' => max(1, floor($currentLevel / 20))
                ];
            }
            
            // Current level practice
            $practiceOptions[] = [
                'title' => 'Practice: ' . $skill->name . ' at Your Level',
                'description' => 'Practice questions matched to your current skill level',
                'difficulty_level' => max(1, min(5, ceil($currentLevel / 20)))
            ];
            
            // Harder practice (if not already at expert level)
            if ($currentLevel < 90) {
                $practiceOptions[] = [
                    'title' => 'Advanced Practice: ' . $skill->name . ' Mastery',
                    'description' => 'Challenge yourself with more difficult questions',
                    'difficulty_level' => min(5, ceil($currentLevel / 20) + 1)
                ];
            }
            
            // Get recommended learning resources for this skill
            // This would typically come from the recommendation system
            $resources = $this->getSkillResources($skillId);
            
            return response()->json([
                'skill_id' => $skillId,
                'skill_name' => $skill->name,
                'current_level' => $currentLevel,
                'practice_options' => $practiceOptions,
                'resources' => $resources
            ]);
        } catch (\Exception $e) {
            Log::error('Error retrieving skill improvement activities: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to retrieve skill improvement activities'], 500);
        }
    }
    
    /**
     * Get learning resources for a specific skill
     *
     * @param int $skillId
     * @return array
     */
    private function getSkillResources($skillId)
    {
        // This would typically query the learning_resources table
        // For now, we'll return sample resources
        
        // Sample resources (in a real implementation, these would come from the database)
        $sampleResources = [
            [
                'id' => 1001,
                'title' => 'Understanding Network Security Fundamentals',
                'description' => 'A comprehensive guide to network security principles',
                'url' => 'https://example.com/resources/network-security-101',
                'type' => 'article'
            ],
            [
                'id' => 1002,
                'title' => 'Hands-on Encryption Workshop',
                'description' => 'Interactive tutorial on encryption technologies',
                'url' => 'https://example.com/workshops/encryption',
                'type' => 'interactive'
            ],
            [
                'id' => 1003,
                'title' => 'Threat Analysis Certification',
                'description' => 'Professional certification course on threat analysis',
                'url' => 'https://example.com/courses/threat-analysis',
                'type' => 'course'
            ]
        ];
        
        // Filter resources relevant to the skill (in a real implementation)
        // For now, we'll just return the samples
        return $sampleResources;
    }
}
         