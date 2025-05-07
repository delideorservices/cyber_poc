<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class UserCertification extends Model
{
    use HasFactory;

    protected $fillable = ['user_id', 'certification_id', 'obtained_date', 'expiry_date'];
    
    protected $casts = [
        'obtained_date' => 'date',
        'expiry_date' => 'date',
    ];
    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function certification()
    {
        return $this->belongsTo(Certification::class);
    }
}