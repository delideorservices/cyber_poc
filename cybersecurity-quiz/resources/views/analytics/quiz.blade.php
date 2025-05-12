@extends('layouts.app')

@section('title', 'Quiz Analytics')

@section('styles')
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.css">
@endsection

@section('content')
<div class="container mx-auto px-4 py-6">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">Quiz Analytics: {{ $quizResult->quiz->title }}</h1>
        <a href="{{ route('analytics.dashboard') }}" class="text-blue-600 hover:text-blue-800">← Back to Dashboard</a>
    </div>
    
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
                <h2 class="text-lg font-semibold text-gray-800 mb-2">Overall Score</h2>
                <p class="text-4xl font-bold {{ $quizResult->percentage_score >= 70 ? 'text-green-600' : 'text-yellow-600' }}">
                    {{ number_format($quizResult->percentage_score, 1) }}%
                </p>
            </div>
            
            <div>
                <h2 class="text-lg font-semibold text-gray-800 mb-2">Points Earned</h2>
                <p class="text-4xl font-bold text-blue-600">
                    {{ $quizResult->points_earned }} / {{ $quizResult->total_points }}
                </p>
            </div>
            
            <div>
                <h2 class="text-lg font-semibold text-gray-800 mb-2">Completed</h2>
                <p class="text-gray-600">{{ $quizResult->created_at->format('M d, Y g:i A') }}</p>
            </div>
        </div>
    </div>
    
    @if(isset($analysis['status']) && $analysis['status'] === 'success')
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <x-analytics.skill-radar-chart 
                chartId="skillRadarChart" 
                :data="$analysis['visualization_data']['radar_chart']"
                title="Skill Performance"
            />
            
            <x-analytics.strength-weakness-chart 
                chartId="strengthWeaknessChart" 
                :data="$analysis['visualization_data']['bar_chart']"
            />
        </div>
        
        <div class="grid grid-cols-1 gap-6 mb-6">
            <x-analytics.peer-comparison
                title="How You Compare to Your Peers"
                :data="$analysis['peer_comparison']"
            />
        </div>
        
        @if(!empty($analysis['chapter_scores']))
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 class="text-lg font-semibold text-gray-800 mb-4">Chapter Performance</h2>
                
                <div class="space-y-4">
                    @foreach($analysis['chapter_scores'] as $chapterScore)
                        <div>
                            <div class="flex justify-between mb-1">
                                <span class="text-sm font-medium text-gray-700">{{ $chapterScore['title'] }}</span>
                                <span class="text-sm font-medium text-gray-700">{{ number_format($chapterScore['score'], 1) }}%</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2.5">
                                <div class="h-2.5 rounded-full {{ $chapterScore['score'] >= 80 ? 'bg-green-600' : ($chapterScore['score'] >= 60 ? 'bg-blue-600' : 'bg-yellow-500') }}" style="width: {{ $chapterScore['score'] }}%"></div>
                            </div>
                        </div>
                    @endforeach
                </div>
            </div>
        @endif
        
        @if(!empty($analysis['recommendations']))
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 class="text-lg font-semibold text-gray-800 mb-4">Improvement Recommendations</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    @foreach($analysis['recommendations'] as $recommendation)
                        <div class="border border-blue-200 rounded-lg p-4 bg-blue-50">
                            <h3 class="font-medium text-blue-800 mb-2">{{ $recommendation['skill_name'] }}</h3>
                            <p class="text-sm text-gray-600 mb-3">{{ $recommendation['message'] }}</p>
                            
                            @if(!empty($recommendation['resources']))
                                <h4 class="text-xs font-semibold text-gray-500 uppercase mb-2">Recommended Resources</h4>
                                <ul class="space-y-1 mb-3">
                                    @foreach($recommendation['resources'] as $resource)
                                        <li>
                                            <a href="{{ $resource['url'] }}" target="_blank" class="text-sm text-blue-600 hover:text-blue-800">
                                                {{ $resource['title'] }}
                                            </a>
                                        </li>
                                    @endforeach
                                </ul>
                            @endif
                            
                            @if(!empty($recommendation['practice_quiz_ids']))
                                <a href="{{ route('quizzes.skill', $recommendation['skill_id']) }}" class="text-sm text-blue-600 font-medium hover:text-blue-800">Practice this skill →</a>
                            @endif
                        </div>
                    @endforeach
                </div>
            </div>
        @endif
        
    @else
        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm text-yellow-700">
                        Enhanced analytics are currently unavailable. Showing basic analysis only.
                    </p>
                </div>
            </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-lg font-semibold text-gray-800 mb-4">Strengths</h2>
                
                @if(empty($analysis['strength_weakness']['strengths']))
                    <p class="text-gray-500 py-4 text-center">No clear strengths identified yet.</p>
                @else
                    <ul class="space-y-2">
                        @foreach($analysis['strength_weakness']['strengths'] as $strength)
                            <li class="flex items-center">
                                <svg class="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                                </svg>
                                <span>{{ $strength['skill_name'] }} ({{ number_format($strength['score'], 1) }}%)</span>
                            </li>
                        @endforeach
                    </ul>
                @endif
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-lg font-semibold text-gray-800 mb-4">Areas for Improvement</h2>
                
                @if(empty($analysis['strength_weakness']['weaknesses']))
                    <p class="text-gray-500 py-4 text-center">No clear weaknesses identified.</p>
                @else
                    <ul class="space-y-2">
                        @foreach($analysis['strength_weakness']['weaknesses'] as $weakness)
                            <li class="flex items-center">
                                <svg class="h-5 w-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                                </svg>
                                <span>{{ $weakness['skill_name'] }} ({{ number_format($weakness['score'], 1) }}%)</span>
                            </li>
                        @endforeach
                    </ul>
                @endif
            </div>
        </div>
    @endif
</div>
@endsection

@section('scripts')
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
@endsection