<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ResourceRecommendation extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'resource_id',
        'status',
        'relevance_score',
        'recommendation_reason',
        'viewed_at',
        'completed_at',
        'user_rating',
        'user_feedback',
        'metadata',
    ];

    protected $casts = [
        'relevance_score' => 'float',
        'viewed_at' => 'datetime',
        'completed_at' => 'datetime',
        'user_rating' => 'integer',
        'metadata' => 'array',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function resource()
    {
        return $this->belongsTo(Resource::class);
    }
}