<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LearningPlanModule extends Model
{
    use HasFactory;

    protected $fillable = [
        'learning_plan_id',
        'title',
        'description',
        'module_type',
        'content_reference_id',
        'sequence',
        'estimated_hours',
        'difficulty_level',
        'required',
        'metadata',
    ];

    protected $casts = [
        'metadata' => 'array',
        'required' => 'boolean',
    ];

    public function learningPlan()
    {
        return $this->belongsTo(LearningPlan::class);
    }

    public function progress()
    {
        return $this->hasMany(LearningPlanProgress::class);
    }
}