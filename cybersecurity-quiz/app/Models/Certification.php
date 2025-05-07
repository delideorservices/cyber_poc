<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Certification extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'provider', 'description'];

    public function users()
    {
        return $this->belongsToMany(User::class, 'user_certifications')
            ->withPivot('obtained_date', 'expiry_date')
            ->withTimestamps();
    }
}