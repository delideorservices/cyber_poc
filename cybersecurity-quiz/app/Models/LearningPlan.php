<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LearningPlan extends Model
{
    use HasFactory;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
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

    /**
     * The attributes that should be cast.
     *
     * @var array
     */
    protected $casts = [
        'focus_areas' => 'array',
        'metadata' => 'array',
        'target_completion_date' => 'datetime',
        'overall_progress' => 'float',
    ];

    /**
     * Get the user that owns the learning plan.
     */
    public function user()
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the modules for the learning plan.
     */
    public function modules()
    {
        return $this->hasMany(LearningPlanModule::class);
    }
}