<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Question extends Model
{
    use HasFactory;

    protected $fillable = [
        'chapter_id', 
        'type', 
        'content', 
        'options', 
        'correct_answer',
        'points',
        'explanation',
        'sequence'
    ];
    
    protected $casts = [
        'options' => 'array',
        'correct_answer' => 'array',
    ];

    public function chapter()
    {
        return $this->belongsTo(Chapter::class);
    }
    
    public function responses()
    {
        return $this->hasMany(UserResponse::class);
    }
    
    // Helper to get quiz through chapter
    public function quiz()
    {
        return $this->chapter->quiz;
    }
}