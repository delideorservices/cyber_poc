<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class AgentLog extends Model
{
    use HasFactory;

    protected $fillable = [
        'agent_name', 
        'action', 
        'input', 
        'output',
        'status',
        'error_message',
        'executed_at'
    ];
    
    protected $casts = [
        'input' => 'array',
        'output' => 'array',
        'executed_at' => 'datetime',
    ];
}