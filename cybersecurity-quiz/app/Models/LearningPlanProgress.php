<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LearningPlanProgress extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'learning_plan_module_id',
        'status',
        'progress_percentage',
        'completed_at',
        'feedback',
        'metadata',
    ];

    protected $casts = [
        'progress_percentage' => 'float',
        'completed_at' => 'datetime',
        'metadata' => 'array',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function module()
    {
        return $this->belongsTo(LearningPlanModule::class, 'learning_plan_module_id');
    }
}