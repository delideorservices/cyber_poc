<?php
/**
 * Skill Heatmap Component
 * 
 * Displays a heatmap visualization of skill proficiency
 * 
 * Props:
 * - data: Array of skills with heat levels
 */
?>

<div class="bg-white p-4 rounded-lg shadow-md">
    <h3 class="text-lg font-semibold mb-4">{{ $title ?? 'Skill Proficiency Heatmap' }}</h3>
    
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        @foreach($data as $skill)
            @php
                $heatClass = match($skill['heat_level']) {
                    0 => 'bg-red-200 border-red-300',
                    1 => 'bg-red-300 border-red-400',
                    2 => 'bg-yellow-200 border-yellow-300',
                    3 => 'bg-green-200 border-green-300',
                    4 => 'bg-green-300 border-green-400',
                    default => 'bg-gray-200 border-gray-300'
                };
            @endphp
            
            <div class="p-3 rounded-lg border {{ $heatClass }} text-center">
                <p class="text-sm font-medium">{{ $skill['skill_name'] }}</p>
                <p class="text-lg font-bold">{{ number_format($skill['score'], 1) }}%</p>
            </div>
        @endforeach
    </div>
    
    <div class="flex justify-center mt-4">
        <div class="flex items-center text-xs text-gray-600">
            <span class="inline-block w-3 h-3 bg-red-200 mr-1 border border-red-300"></span>
            <span class="mr-3">Beginner</span>
            
            <span class="inline-block w-3 h-3 bg-yellow-200 mr-1 border border-yellow-300"></span>
            <span class="mr-3">Intermediate</span>
            
            <span class="inline-block w-3 h-3 bg-green-300 mr-1 border border-green-400"></span>
            <span>Advanced</span>
        </div>
    </div>
</div>