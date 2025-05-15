<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LearningPlan extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'title',
        'description',
        'focus_areas',
        'target_completion_date',
        'status',
        'difficulty_level',
        'overall_progress',
        'metadata',
    ];

    protected $casts = [
        'focus_areas' => 'array',
        'metadata' => 'array',
        'target_completion_date' => 'datetime',
        'overall_progress' => 'float',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function modules()
    {
        return $this->hasMany(LearningPlanModule::class);
    }
}