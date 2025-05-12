<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Recommendation extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'learning_resource_id',
        'relevance_score',
        'targeted_skills',
        'recommendation_reason',
        'is_viewed',
        'is_completed',
        'recommended_at',
        'completed_at',
    ];

    protected $casts = [
        'targeted_skills' => 'array',
        'is_viewed' => 'boolean',
        'is_completed' => 'boolean',
        'recommended_at' => 'datetime',
        'completed_at' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function learningResource()
    {
        return $this->belongsTo(LearningResource::class);
    }
}