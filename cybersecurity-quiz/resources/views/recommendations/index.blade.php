@extends('layouts.app')

@section('content')
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-10">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Your Personalized Learning Recommendations</h5>
                    <form action="{{ route('recommendations.generate') }}" method="POST">
                        @csrf
                        <button type="submit" class="btn btn-sm btn-primary">
                            <i class="fas fa-sync-alt"></i> Refresh Recommendations
                        </button>
                    </form>
                </div>

                @if(session('success'))
                    <div class="alert alert-success">{{ session('success') }}</div>
                @endif

                @if(session('error'))
                    <div class="alert alert-danger">{{ session('error') }}</div>
                @endif

                @if(count($skillGaps) > 0)
                    <div class="card-body">
                        <h6>Based on your skill gaps:</h6>
                        <div class="mb-4">
                            <div class="row">
                                @foreach($skillGaps as $gap)
                                    <div class="col-md-4 mb-2">
                                        <div class="d-flex align-items-center">
                                            <span class="badge bg-primary me-2">{{ $gap['skill_name'] }}</span>
                                            <div class="progress flex-grow-1" style="height: 8px;">
                                                <div class="progress-bar" role="progressbar" style="width: {{ ($gap['current_proficiency'] / 5) * 100 }}%"></div>
                                            </div>
                                        </div>
                                    </div>
                                @endforeach
                            </div>
                        </div>
                    </div>
                @endif

                <div class="card-body p-0">
                    @if(count($recommendations) > 0)
                        <div class="list-group list-group-flush">
                            @foreach($recommendations as $recommendation)
                                <div class="list-group-item {{ $recommendation->is_completed ? 'bg-light' : '' }}">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <h5 class="mb-1">
                                            @if($recommendation->is_completed)
                                                <i class="fas fa-check-circle text-success"></i>
                                            @endif
                                            {{ $recommendation->learningResource->title }}
                                        </h5>
                                        <span class="badge bg-info text-white">
                                            {{ ucfirst($recommendation->learningResource->resource_type) }}
                                        </span>
                                    </div>

                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <div>
                                            <small class="text-muted">
                                                <i class="far fa-clock"></i> {{ $recommendation->learningResource->estimated_minutes }} minutes
                                            </small>
                                        </div>
                                        <div>
                                            <small>Difficulty:</small>
                                            <span class="ms-1">
                                                @for($i = 1; $i <= 5; $i++)
                                                    <i class="fas fa-circle {{ $i <= $recommendation->learningResource->difficulty_level ? 'text-primary' : 'text-muted opacity-25' }}" style="font-size: 8px;"></i>
                                                @endfor
                                            </span>
                                        </div>
                                        <div>
                                            <span class="badge bg-success">{{ round($recommendation->relevance_score) }}% Match</span>
                                        </div>
                                    </div>

                                    <p class="mb-2">{{ $recommendation->learningResource->description }}</p>

                                    <div class="alert alert-light mb-2">
                                        <i class="fas fa-lightbulb text-warning"></i> <small>{{ $recommendation->recommendation_reason }}</small>
                                    </div>

                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            @foreach(json_decode($recommendation->targeted_skills) as $skillId)
                                                @foreach($skillGaps as $gap)
                                                    @if($gap['skill_id'] == $skillId)
                                                        <span class="badge bg-secondary me-1">{{ $gap['skill_name'] }}</span>
                                                    @endif
                                                @endforeach
                                            @endforeach
                                        </div>

                                        <div>
                                            @if(!$recommendation->is_completed)
                                                <a href="{{ $recommendation->learningResource->url }}" target="_blank" class="btn btn-primary btn-sm view-resource" data-recommendation-id="{{ $recommendation->id }}">
                                                    <i class="fas fa-external-link-alt"></i> View Resource
                                                </a>
                                                <form method="POST" action="{{ route('recommendations.completed', $recommendation->id) }}" class="d-inline">
                                                    @csrf
                                                    <button type="submit" class="btn btn-outline-success btn-sm ms-2">
                                                        <i class="fas fa-check"></i> Mark Complete
                                                    </button>
                                                </form>
                                            @else
                                                <a href="{{ $recommendation->learningResource->url }}" target="_blank" class="btn btn-outline-secondary btn-sm">
                                                    <i class="fas fa-external-link-alt"></i> Review Again
                                                </a>
                                                <small class="text-muted ms-2">
                                                    Completed {{ $recommendation->completed_at->diffForHumans() }}
                                                </small>
                                            @endif
                                        </div>
                                    </div>
                                </div>
                            @endforeach
                        </div>
                    @else
                        <div class="text-center p-5">
                            <i class="fas fa-lightbulb text-muted" style="font-size: 48px;"></i>
                            <h4 class="mt-3">No recommendations yet</h4>
                            <p class="text-muted">Complete more quizzes to get personalized recommendations.</p>
                            <a href="{{ route('quizzes.index') }}" class="btn btn-primary mt-2">
                                <i class="fas fa-puzzle-piece"></i> Take a Quiz
                            </a>
                        </div>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Mark recommendation as viewed when clicking on the view resource button
        document.querySelectorAll('.view-resource').forEach(function(button) {
            button.addEventListener('click', function() {
                const recommendationId = this.getAttribute('data-recommendation-id');
                fetch(`/recommendations/${recommendationId}/viewed`, {
                    method: 'POST',
                    headers: {
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                });
            });
        });
    });
</script>
@endpush