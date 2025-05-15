<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Resource extends Model
{
    use HasFactory;

    protected $fillable = [
        'title',
        'description',
        'resource_type',
        'url',
        'author',
        'publisher',
        'published_date',
        'duration_minutes',
        'difficulty_level',
        'tags',
        'metadata',
    ];

    protected $casts = [
        'published_date' => 'date',
        'duration_minutes' => 'integer',
        'difficulty_level' => 'integer',
        'tags' => 'array',
        'metadata' => 'array',
    ];

    public function skills()
    {
        return $this->belongsToMany(Skill::class, 'resource_skills');
    }

    public function recommendations()
    {
        return $this->hasMany(ResourceRecommendation::class);
    }
}