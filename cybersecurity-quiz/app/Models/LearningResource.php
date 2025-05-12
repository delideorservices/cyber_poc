<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LearningResource extends Model
{
    use HasFactory;

    protected $fillable = [
        'title',
        'description',
        'resource_type',
        'url',
        'difficulty_level',
        'sector_id',
        'skill_tags',
        'topic_tags',
        'estimated_minutes',
        'is_premium',
    ];

    protected $casts = [
        'skill_tags' => 'array',
        'topic_tags' => 'array',
        'is_premium' => 'boolean',
    ];

    public function sector()
    {
        return $this->belongsTo(Sector::class);
    }

    public function recommendations()
    {
        return $this->hasMany(Recommendation::class);
    }
}