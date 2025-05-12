@extends('layouts.app')

@section('content')
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>{{ __('Your Cybersecurity Skills Analytics') }}</h1>
            
            @if(isset($skillAnalytics) && $skillAnalytics)
                <div class="analytics-summary">
                    <div class="card">
                        <div class="card-body">
                            <h3>{{ __('Overall Progress') }}</h3>
                            <div class="progress mb-3">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: {{ $skillAnalytics->overall_percentage }}%"
                                     aria-valuenow="{{ $skillAnalytics->overall_percentage }}" 
                                     aria-valuemin="0" aria-valuemax="100">
                                    {{ $skillAnalytics->overall_percentage }}%
                                </div>
                            </div>
                            
                            <div class="analytics-metrics">
                                <div class="metric">
                                    <span class="metric-label">{{ __('Quizzes Completed') }}:</span>
                                    <span class="metric-value">{{ $skillAnalytics->quizzes_completed }}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">{{ __('Total Score') }}:</span>
                                    <span class="metric-value">{{ $skillAnalytics->total_points }} {{ __('points') }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                @if(count($skillAnalytics->domain_scores) > 0)
                    <div class="domain-analysis">
                        <h3>{{ __('Domain Proficiency') }}</h3>
                        
                        @foreach($skillAnalytics->domain_scores as $domain)
                            @include('analytics.domain-card', ['domain' => $domain])
                        @endforeach
                    </div>
                @endif
                
                @if(count($skillAnalytics->strength_areas) > 0 || count($skillAnalytics->improvement_areas) > 0)
                    <div class="row mt-4">
                        <div class="col-md-6">
                            @include('analytics.strengths', ['strengths' => $skillAnalytics->strength_areas])
                        </div>
                        <div class="col-md-6">
                            @include('analytics.improvements', ['improvements' => $skillAnalytics->improvement_areas])
                        </div>
                    </div>
                @endif
                
                @if(isset($skillAnalytics->trend_data) && $skillAnalytics->trend_data)
                    <div class="progress-trend mt-4">
                        <h3>{{ __('Your Progress Over Time') }}</h3>
                        <div id="progress-chart-container" data-chart-data="{{ json_encode($skillAnalytics->trend_data) }}"></div>
                    </div>
                @endif
                
            @else
                <div class="alert alert-info">
                    {{ __('Complete at least one quiz to see your analytics dashboard.') }}
                </div>
                
                @if(isset($availableQuiz) && $availableQuiz)
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">{{ __('Start building your skills profile') }}</h5>
                            <p>{{ __('Take your first cybersecurity assessment to see your analytics.') }}</p>
                            <a href="{{ route('quizzes.start', $availableQuiz->id) }}" class="btn btn-primary">
                                {{ __('Start Assessment') }}
                            </a>
                        </div>
                    </div>
                @endif
            @endif
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script>
    // This script will be responsible for rendering analytics charts using the data attributes
    document.addEventListener('DOMContentLoaded', function() {
        const chartContainer = document.getElementById('progress-chart-container');
        if (chartContainer) {
            const chartData = JSON.parse(chartContainer.getAttribute('data-chart-data'));
            // Initialize chart with chartData
            // Example using ChartJS (would need to be included in the main layout)
            // renderProgressChart(chartContainer, chartData);
        }
    });
</script>
@endpush