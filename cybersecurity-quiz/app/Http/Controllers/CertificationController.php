<?php

namespace App\Http\Controllers;

use App\Models\Certification;
use Illuminate\Http\Request;

class CertificationController extends Controller
{
    public function index()
    {
        $certifications = Certification::all();
        return response()->json($certifications);
    }
    
    public function show(Certification $certification)
    {
        return response()->json($certification);
    }
}