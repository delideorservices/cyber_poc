<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Topic extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'description', 'sector_id', 'keywords'];
    
    protected $casts = [
        'keywords' => 'array',
    ];

    public function sector()
    {
        return $this->belongsTo(Sector::class);
    }
    
    public function quizzes()
    {
        return $this->hasMany(Quiz::class);
    }
}