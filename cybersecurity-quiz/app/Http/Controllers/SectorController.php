<?php

namespace App\Http\Controllers;

use App\Models\Sector;
use Illuminate\Http\Request;

class SectorController extends Controller
{
    public function index()
    {
        $sectors = Sector::all();
        return response()->json($sectors);
    }
    
    public function show(Sector $sector)
    {
        return response()->json($sector);
    }
}