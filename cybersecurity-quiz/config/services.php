<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Mailgun, Postmark, AWS and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'mailgun' => [
        'domain' => env('MAILGUN_DOMAIN'),
        'secret' => env('MAILGUN_SECRET'),
        'endpoint' => env('MAILGUN_ENDPOINT', 'api.mailgun.net'),
        'scheme' => 'https',
    ],

    'postmark' => [
        'token' => env('POSTMARK_TOKEN'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],
    'ai_backend' => [
        'url' => env('AI_BACKEND_URL', 'http://localhost:8001'),
        'timeout' => env('AI_BACKEND_TIMEOUT', 300),
    ],
    'agents' => [
        'url' => env('AGENT_SERVICE_URL', 'http://localhost:8001'),
        'timeout' => env('AGENT_SERVICE_TIMEOUT', 60),
        'cache' => [
            'enabled' => env('AGENT_CACHE_ENABLED', true),
            'ttl' => env('AGENT_CACHE_TTL', 3600)
        ],
        'monitoring' => [
            'enabled' => env('AGENT_MONITORING_ENABLED', true),
            'threshold_ms' => env('AGENT_SLOW_THRESHOLD_MS', 2000)
        ],
        'retry' => [
            'max_attempts' => env('AGENT_RETRY_MAX', 3),
            'backoff_factor' => env('AGENT_RETRY_BACKOFF', 2)
        ]
    ],

];
