<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Role extends Model
{
    use HasFactory;

    protected $fillable = ['sector_id', 'name', 'description'];

    public function sector()
    {
        return $this->belongsTo(Sector::class);
    }

    public function users()
    {
        return $this->hasMany(User::class);
    }
}