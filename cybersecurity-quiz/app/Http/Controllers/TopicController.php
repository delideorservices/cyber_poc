<?php

namespace App\Http\Controllers;

use App\Models\Topic;
use Illuminate\Http\Request;

class TopicController extends Controller
{
    public function index(Request $request)
    {
        $query = Topic::query();
        
        // Filter by sector if provided
        if ($request->has('sector_id')) {
            $query->where(function($q) use ($request) {
                $q->where('sector_id', $request->sector_id)
                  ->orWhereNull('sector_id');
            });
        }
        
        // Search by keyword
        if ($request->has('search')) {
            $search = $request->search;
            $query->where(function($q) use ($search) {
                $q->where('name', 'like', "%{$search}%")
                  ->orWhere('description', 'like', "%{$search}%")
                  ->orWhereRaw("keywords::text ILIKE ?", ["%{$search}%"]);
            });
        }
        
        $topics = $query->get();
        return response()->json($topics);
    }
    
    public function show(Topic $topic)
    {
        return response()->json($topic);
    }
}