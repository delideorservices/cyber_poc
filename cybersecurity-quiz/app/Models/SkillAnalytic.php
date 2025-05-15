<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SkillAnalytic extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'skill_id',
        'proficiency_score',
        'strength_level',
        'is_strength',
        'is_weakness',
        'benchmark_percentile',
        'sector_benchmark',
        'trend_direction',
        'last_updated',
        'metadata',
    ];

    protected $casts = [
        'proficiency_score' => 'float',
        'strength_level' => 'integer',
        'is_strength' => 'boolean',
        'is_weakness' => 'boolean',
        'benchmark_percentile' => 'float',
        'sector_benchmark' => 'float',
        'last_updated' => 'datetime',
        'metadata' => 'array',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function skill()
    {
        return $this->belongsTo(Skill::class);
    }
}