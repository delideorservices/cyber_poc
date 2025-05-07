<?php

namespace App\Http\Controllers;

use App\Models\Role;
use Illuminate\Http\Request;

class RoleController extends Controller
{
    public function index(Request $request)
    {
        $query = Role::query();
        
        // Filter by sector if provided
        if ($request->has('sector_id')) {
            $query->where('sector_id', $request->sector_id);
        }
        
        $roles = $query->get();
        return response()->json($roles);
    }
    
    public function show(Role $role)
    {
        return response()->json($role);
    }
}