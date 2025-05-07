<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Chapter extends Model
{
    use HasFactory;

    protected $fillable = ['quiz_id', 'title', 'description', 'sequence'];

    public function quiz()
    {
        return $this->belongsTo(Quiz::class);
    }
    
    public function questions()
    {
        return $this->hasMany(Question::class)->orderBy('sequence');
    }
}