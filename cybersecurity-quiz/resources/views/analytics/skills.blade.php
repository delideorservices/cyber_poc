@extends('layouts.app')

@section('title', 'Skill Analytics')

@section('styles')
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.css">
@endsection

@section('content')
<div class="container mx-auto px-4 py-6">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">Skill Analytics Dashboard</h1>
        <a href="{{ route('analytics.dashboard') }}" class="text-blue-600 hover:text-blue-800">← Back to Dashboard</a>
    </div>
    
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Skill Proficiency Overview</h2>
            
            @if(empty($skillPerformance))
                <p class="text-gray-500 py-8 text-center">Complete quizzes to see your skill proficiency data.</p>
            @else
                <div class="h-64">
                    <canvas id="skillProficiencyChart"></canvas>
                </div>
                
                @push('scripts')
                <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        const ctx = document.getElementById('skillProficiencyChart').getContext('2d');
                        const chartData = {
                            labels: [
                                @foreach($skillPerformance as $skill)
                                    "{{ $skill->skill_name }}",
                                @endforeach
                            ],
                            datasets: [{
                                label: 'Proficiency (%)',
                                data: [
                                    @foreach($skillPerformance as $skill)
                                        {{ number_format($skill->score_percentage, 1) }},
                                    @endforeach
                                ],
                                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                borderColor: 'rgb(54, 162, 235)',
                                borderWidth: 2,
                                pointBackgroundColor: 'rgb(54, 162, 235)',
                                pointBorderColor: '#fff',
                                pointHoverBackgroundColor: '#fff',
                                pointHoverBorderColor: 'rgb(54, 162, 235)'
                            }]
                        };
                        
                        new Chart(ctx, {
                            type: 'radar',
                            data: chartData,
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    r: {
                                        angleLines: {
                                            display: true
                                        },
                                        suggestedMin: 0,
                                        suggestedMax: 100
                                    }
                                }
                            }
                        });
                    });
                </script>
                @endpush
            @endif
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Skill Heatmap</h2>
            
            @if(empty($skillPerformance))
                <p class="text-gray-500 py-8 text-center">Complete quizzes to see your skill heatmap.</p>
            @else
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    @foreach($skillPerformance as $skill)
                        @php
                            if ($skill->score_percentage >= 80) {
                                $class = 'bg-green-100 border-green-300 text-green-800';
                            } elseif ($skill->score_percentage >= 60) {
                                $class = 'bg-blue-100 border-blue-300 text-blue-800';
                            } elseif ($skill->score_percentage >= 40) {
                                $class = 'bg-yellow-100 border-yellow-300 text-yellow-800';
                            } else {
                                $class = 'bg-red-100 border-red-300 text-red-800';
                            }
                        @endphp
                        
                        <div class="border rounded-lg p-3 {{ $class }}">
                            <p class="text-sm font-medium">{{ $skill->skill_name }}</p>
                            <p class="text-lg font-bold">{{ number_format($skill->score_percentage, 1) }}%</p>
                            <p class="text-xs">{{ $skill->correct_answers }} / {{ $skill->total_questions }} correct</p>
                        </div>
                    @endforeach
                </div>
                
                <div class="flex justify-center mt-4">
                    <div class="flex items-center text-xs text-gray-600">
                        <span class="inline-block w-3 h-3 bg-red-100 mr-1 border border-red-300"></span>
                        <span class="mr-3">Needs Work (0-40%)</span>
                        
                        <span class="inline-block w-3 h-3 bg-yellow-100 mr-1 border border-yellow-300"></span>
                        <span class="mr-3">Developing (40-60%)</span>
                        
                        <span class="inline-block w-3 h-3 bg-blue-100 mr-1 border border-blue-300"></span>
                        <span class="mr-3">Proficient (60-80%)</span>
                        
                        <span class="inline-block w-3 h-3 bg-green-100 mr-1 border border-green-300"></span>
                        <span>Advanced (80-100%)</span>
                    </div>
                </div>
            @endif
        </div>
    </div>
    
    <div class="grid grid-cols-1 gap-6 mb-6">
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Peer Comparison</h2>
            
            @if(isset($peerComparison['status']) && $peerComparison['status'] == 'insufficient_data')
                <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                    <p class="text-sm text-yellow-700">{{ $peerComparison['message'] }}</p>
                </div>
            @elseif(empty($peerComparison['skill_comparison']))
                <p class="text-gray-500 py-4 text-center">Complete more quizzes to enable peer comparison.</p>
            @else
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead>
                            <tr>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Skill</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Your Score</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Peer Average</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difference</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Percentile</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            @foreach($peerComparison['skill_comparison'] as $comparison)
                                <tr>
                                    <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ $comparison['skill_name'] }}</td>
                                    <td class="px-4 py-3 text-sm text-gray-900">{{ number_format($comparison['user_score'], 1) }}%</td>
                                    <td class="px-4 py-3 text-sm text-gray-500">{{ number_format($comparison['peer_average'], 1) }}%</td>
                                    <td class="px-4 py-3 text-sm">
                                        <span class="{{ $comparison['differential'] >= 0 ? 'text-green-600' : 'text-red-600' }}">
                                            {{ $comparison['differential'] >= 0 ? '+' : '' }}{{ number_format($comparison['differential'], 1) }}%
                                        </span>
                                    </td>
                                    <td class="px-4 py-3 text-sm text-gray-900">{{ number_format($comparison['percentile'], 1) }}</td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
                
                <p class="text-xs text-gray-500 mt-3">Based on comparison with {{ $peerComparison['peer_count'] }} peers with similar roles and experience.</p>
            @endif
        </div>
    </div>
    
    <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Recommended Learning Paths</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            @if(empty($skillPerformance))
                <div class="col-span-3">
                    <p class="text-gray-500 py-4 text-center">Complete quizzes to get personalized learning path recommendations.</p>
                </div>
            @else
                @php
                    // Example learning paths based on skill performance
                    $weakestSkills = collect($skillPerformance)
                        ->sortBy('score_percentage')
                        ->take(3);
                @endphp
                
                @foreach($weakestSkills as $skill)
                    <div class="border border-blue-200 rounded-lg p-4 bg-blue-50">
                        <h3 class="font-medium text-blue-800 mb-2">{{ $skill->skill_name }} Path</h3>
                        <p class="text-sm text-gray-600 mb-3">Improve your {{ $skill->skill_name }} skills with targeted learning resources and practice.</p>
                        <a href="{{ route('skills.show', $skill->skill_id) }}" class="text-sm text-blue-600 font-medium hover:text-blue-800">Start Learning →</a>
                    </div>
                @endforeach
            @endif
        </div>
    </div>
</div>
@endsection

@section('scripts')
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
@endsection