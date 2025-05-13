<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Cache;

class AgentService
{
    protected $baseUrl;
    protected $timeout;
    
    public function __construct()
    {
        $this->baseUrl = config('services.agents.url', 'http://localhost:5000');
        $this->timeout = config('services.agents.timeout', 30);
    }
    
    /**
     * Execute an agent with the given name and data
     * 
     * @param string $agentName
     * @param array $data
     * @return array
     */
    public function executeAgent($agentName, $data)
    {
        try {
            // Log request for debugging
            Log::channel('agent')->info("Calling agent: {$agentName}", [
                'data' => $data
            ]);
            
            // Make HTTP request to Python agent service
            $response = Http::timeout($this->timeout)
                ->post("{$this->baseUrl}/api/agent/{$agentName}", $data);
            
            if ($response->successful()) {
                Log::channel('agent')->info("Agent response successful: {$agentName}");
                
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            } else {
                Log::channel('agent')->error("Agent execution failed: {$agentName}", [
                    'status' => $response->status(),
                    'response' => $response->body()
                ]);
                
                return [
                    'success' => false,
                    'error' => "Agent execution failed: {$response->status()}",
                    'details' => $response->json() ?? ['message' => 'No response details available']
                ];
            }
        } catch (\Exception $e) {
            Log::channel('agent')->error("Agent communication error: {$agentName}", [
                'error' => $e->getMessage()
            ]);
            
            return [
                'success' => false,
                'error' => 'Agent service communication error',
                'message' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Get cached agent result to avoid repeated calls
     * 
     * @param string $key
     * @param string $agentName
     * @param array $data
     * @param int $ttl
     * @return array
     */
    public function getCachedAgentResult($key, $agentName, $data, $ttl = 3600)
    {
        return Cache::remember($key, $ttl, function () use ($agentName, $data) {
            return $this->executeAgent($agentName, $data);
        });
    }
}