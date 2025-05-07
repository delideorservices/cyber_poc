<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class UserQuizResult extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 
        'quiz_id', 
        'total_points', 
        'points_earned',
        'percentage_score',
        'chapter_scores',
        'skill_gaps',
        'feedback',
        'completed_at'
    ];
    
    protected $casts = [
        'chapter_scores' => 'array',
        'skill_gaps' => 'array',
        'completed_at' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
    
    public function quiz()
    {
        return $this->belongsTo(Quiz::class);
    }
}