@extends('layouts.app')

@section('content')
<div class="container">
    <div class="row">
        <div class="col-md-12">
            @if(isset($practice) && $practice)
                <div class="practice-header">
                    <h1>{{ $practice->title }}</h1>
                    <p>{{ $practice->description }}</p>
                    
                    @if(isset($practice->skill))
                        <div class="related-skill mb-3">
                            <span class="badge badge-info">{{ __('Skill') }}: {{ $practice->skill->name }}</span>
                            @if(isset($practice->difficulty))
                                <span class="badge badge-secondary">
                                    {{ __('Difficulty') }}: {{ $practice->difficulty }}/5
                                </span>
                            @endif
                        </div>
                    @endif
                </div>
                
                <div class="practice-content">
                    @if($practice->type == 'quiz')
                        @include('skill-improvement.practice-types.quiz', ['practice' => $practice])
                    @elseif($practice->type == 'challenge')
                        @include('skill-improvement.practice-types.challenge', ['practice' => $practice])
                    @elseif($practice->type == 'exercise')
                        @include('skill-improvement.practice-types.exercise', ['practice' => $practice])
                    @else
                        <div class="alert alert-warning">
                            {{ __('Unknown practice type.') }}
                        </div>
                    @endif
                </div>
                
                @if(isset($practice->spaced_repetition) && $practice->spaced_repetition)
                    <div class="spaced-repetition-info mt-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">{{ __('Spaced Repetition Schedule') }}</h5>
                                <p>{{ __('To strengthen your memory and skill retention, we recommend practicing this again on:') }}</p>
                                <ul class="list-group">
                                    @foreach($practice->spaced_repetition as $index => $date)
                                        <li class="list-group-item">
                                            {{ __('Review') }} {{ $index + 1 }}: {{ $date->format('F j, Y') }}
                                        </li>
                                    @endforeach
                                </ul>
                                <div class="mt-3">
                                    <button type="button" class="btn btn-sm btn-outline-primary add-to-calendar" 
                                           data-practice-id="{{ $practice->id }}">
                                        {{ __('Add to Calendar') }}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                @endif
                
                @if(isset($practice->related_practices) && count($practice->related_practices) > 0)
                    <div class="related-practices mt-4">
                        <h3>{{ __('Related Practice Activities') }}</h3>
                        <div class="row">
                            @foreach($practice->related_practices as $related)
                                <div class="col-md-4 mb-3">
                                    <div class="card">
                                        <div class="card-body">
                                            <h5 class="card-title">{{ $related->title }}</h5>
                                            <p class="card-text">{{ Str::limit($related->description, 100) }}</p>
                                            <a href="{{ route('skill-improvement.practice', $related->id) }}" 
                                               class="btn btn-sm btn-primary">
                                                {{ __('Start Practice') }}
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endif
            @else
                <div class="alert alert-danger">
                    {{ __('Practice activity not found.') }}
                </div>
                <a href="{{ route('skill-improvement.index') }}" class="btn btn-primary">
                    {{ __('Return to Skill Improvement') }}
                </a>
            @endif
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Handles the add to calendar button functionality
        const addToCalendarBtn = document.querySelector('.add-to-calendar');
        if (addToCalendarBtn) {
            addToCalendarBtn.addEventListener('click', function() {
                const practiceId = this.getAttribute('data-practice-id');
                // AJAX call to add practice to calendar
                fetch(`/skill-improvement/calendar-add/${practiceId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('{{ __("Practice sessions added to your calendar!") }}');
                    } else {
                        alert('{{ __("Failed to add to calendar. Please try again.") }}');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('{{ __("An error occurred. Please try again.") }}');
                });
            });
        }
    });
</script>
@endpush