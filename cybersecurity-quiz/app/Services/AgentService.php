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
 public function executeAgent($agentName, $data, $retryCount = 0)
{
    try {
        // Log request for debugging
        Log::channel('agent')->info("Calling agent: {$agentName}", [
            'attempt' => $retryCount + 1,
            'data' => $data
        ]);
        
        // Start timing
        $startTime = microtime(true);
        
        // Make HTTP request to Python agent service
        $response = Http::timeout($this->timeout)
            ->withHeaders([
                'X-Agent-Request-ID' => uniqid('agent_req_'),
                'X-Retry-Count' => $retryCount
            ])
            ->post("{$this->baseUrl}/api/agent/{$agentName}", $data);
        
        // Calculate response time
        $responseTime = microtime(true) - $startTime;
        
        // Log performance metrics
        Log::channel('agent')->info("Agent response time: {$agentName}", [
            'response_time_ms' => round($responseTime * 1000),
            'status' => $response->status()
        ]);
        
        if ($response->successful()) {
            Log::channel('agent')->info("Agent response successful: {$agentName}");
            
            // Monitor slow responses
            if ($responseTime > 2.0) { // Threshold of 2 seconds
                Log::channel('agent')->warning("Slow agent response: {$agentName}", [
                    'response_time_ms' => round($responseTime * 1000)
                ]);
            }
            
            return [
                'success' => true,
                'data' => $response->json(),
                'response_time_ms' => round($responseTime * 1000)
            ];
        } else {
            Log::channel('agent')->error("Agent execution failed: {$agentName}", [
                'status' => $response->status(),
                'response' => $response->body()
            ]);
            
            // Retry logic for 5xx errors (server errors)
            if ($response->serverError() && $retryCount < 2) {
                Log::channel('agent')->info("Retrying agent call: {$agentName}", [
                    'retry_count' => $retryCount + 1
                ]);
                
                // Exponential backoff (wait longer between retries)
                sleep(pow(2, $retryCount));
                
                // Recursive retry with incremented count
                return $this->executeAgent($agentName, $data, $retryCount + 1);
            }
            
            return [
                'success' => false,
                'error' => "Agent execution failed: {$response->status()}",
                'details' => $response->json() ?? ['message' => 'No response details available'],
                'status_code' => $response->status()
            ];
        }
    } catch (\Exception $e) {
        Log::channel('agent')->error("Agent communication error: {$agentName}", [
            'error' => $e->getMessage(),
            'trace' => $e->getTraceAsString()
        ]);
        
        // Retry network errors
        if (($e instanceof \Illuminate\Http\Client\ConnectionException || 
             $e instanceof \GuzzleHttp\Exception\ConnectException) && 
            $retryCount < 2) {
            
            Log::channel('agent')->info("Retrying after connection error: {$agentName}", [
                'retry_count' => $retryCount + 1
            ]);
            
            // Exponential backoff
            sleep(pow(2, $retryCount));
            
            // Recursive retry
            return $this->executeAgent($agentName, $data, $retryCount + 1);
        }
        
        return [
            'success' => false,
            'error' => 'Agent service communication error',
            'message' => $e->getMessage(),
            'exception_class' => get_class($e)
        ];
    }
}
public function executeBatchAgents($agentCalls)
{
    $results = [];
    $allSuccessful = true;
    
    foreach ($agentCalls as $key => $call) {
        if (!isset($call['agent']) || !isset($call['data'])) {
            $results[$key] = [
                'success' => false,
                'error' => 'Invalid agent call format'
            ];
            $allSuccessful = false;
            continue;
        }
        
        $result = $this->executeAgent($call['agent'], $call['data']);
        $results[$key] = $result;
        
        if (!$result['success']) {
            $allSuccessful = false;
        }
    }
    
    return [
        'success' => $allSuccessful,
        'results' => $results
    ];
}

/**
 * Execute agents in parallel
 *
 * @param array $agentCalls Array of ['agent' => 'agent_name', 'data' => [...]]
 * @return array
 */
public function executeParallelAgents($agentCalls)
{
    $promises = [];
    
    foreach ($agentCalls as $key => $call) {
        if (!isset($call['agent']) || !isset($call['data'])) {
            continue;
        }
        
        $agentName = $call['agent'];
        $data = $call['data'];
        
        // Create promise for async HTTP request
        $promises[$key] = Http::async()
            ->timeout($this->timeout)
            ->withHeaders([
                'X-Agent-Request-ID' => uniqid('agent_req_'),
                'X-Execution-Type' => 'parallel'
            ])
            ->post("{$this->baseUrl}/api/agent/{$agentName}", $data);
    }
    
    // Wait for all promises to complete
    $responses = [];
    foreach ($promises as $key => $promise) {
        try {
            $response = $promise->wait();
            
            if ($response->successful()) {
                $responses[$key] = [
                    'success' => true,
                    'data' => $response->json()
                ];
            } else {
                $responses[$key] = [
                    'success' => false,
                    'error' => "Agent execution failed: {$response->status()}",
                    'details' => $response->json() ?? ['message' => 'No response details available']
                ];
            }
        } catch (\Exception $e) {
            $responses[$key] = [
                'success' => false,
                'error' => 'Agent service communication error',
                'message' => $e->getMessage()
            ];
        }
    }
    
    return $responses;
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