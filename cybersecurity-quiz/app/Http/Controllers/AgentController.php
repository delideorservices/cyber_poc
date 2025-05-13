<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class AgentController extends Controller
{
    protected $agentBaseUrl;
    
    public function __construct()
    {
        $this->agentBaseUrl = env('AGENT_SERVICE_URL', 'http://localhost:5000');
    }
    
    public function executeAgent(Request $request, $agentName)
    {
        $validatedData = $request->validate([
            'user_id' => 'required|integer',
            'data' => 'required|array'
        ]);
        
        try {
            $response = Http::post("{$this->agentBaseUrl}/api/agent/{$agentName}", [
                'user_id' => $validatedData['user_id'],
                'data' => $validatedData['data']
            ]);
            
            if ($response->successful()) {
                return response()->json($response->json());
            } else {
                return response()->json([
                    'error' => 'Agent execution failed',
                    'details' => $response->json()
                ], $response->status());
            }
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Agent service communication error',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function generateLearningPlan(Request $request)
    {
        $user = auth()->user();
        
        return $this->executeAgent($request, 'learning_plan_agent');
    }
    
    public function analyzeUserSkills(Request $request)
    {
        $user = auth()->user();
        
        return $this->executeAgent($request, 'analytics_agent');
    }
    
    public function getSkillImprovementPlan(Request $request)
    {
        $user = auth()->user();
        
        return $this->executeAgent($request, 'skill_improvement_agent');
    }
    
    public function generateRecommendations(Request $request)
    {
        $user = auth()->user();
        
        return $this->executeAgent($request, 'recommendation_agent');
    }
}