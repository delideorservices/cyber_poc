<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Quiz extends Model
{
    use HasFactory;

    protected $fillable = [
        'title', 
        'description', 
        'user_id', 
        'topic_id', 
        'sector_id', 
        'role_id', 
        'difficulty_level',
        'metadata'
    ];
    
    protected $casts = [
        'metadata' => 'array',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
    
    public function topic()
    {
        return $this->belongsTo(Topic::class);
    }
    
    public function sector()
    {
        return $this->belongsTo(Sector::class);
    }
    
    public function role()
    {
        return $this->belongsTo(Role::class);
    }
    
    public function chapters()
    {
        return $this->hasMany(Chapter::class)->orderBy('sequence');
    }
    
    public function results()
    {
        return $this->hasMany(UserQuizResult::class);
    }
    
    // Helper to get all questions across all chapters
    public function getAllQuestions()
    {
        return Question::whereIn('chapter_id', $this->chapters->pluck('id'))->orderBy('sequence')->get();
    }
}