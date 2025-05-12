<!-- Learning Plan Content Partial View -->
<div class="learning-plan-container" id="learning-plan-{{ $plan->id }}">
    <div class="plan-header">
        <h2>{{ $plan->title }}</h2>
        <p>{{ $plan->description }}</p>
        
        @if($plan->last_updated)
            <div class="plan-meta">
                {{ __('Last updated') }}: {{ $plan->last_updated->diffForHumans() }}
            </div>
        @endif
    </div>
    
    <div class="plan-progress">
        <div class="progress">
            <div class="progress-bar" role="progressbar" style="width: {{ $plan->completion_percentage }}%"
                 aria-valuenow="{{ $plan->completion_percentage }}" aria-valuemin="0" aria-valuemax="100">
                {{ $plan->completion_percentage }}%
            </div>
        </div>
    </div>
    
    @if(count($plan->milestones) > 0)
        <div class="milestones-container">
            @foreach($plan->milestones as $milestone)
                @include('learning-plan.milestone', ['milestone' => $milestone])
            @endforeach
        </div>
    @else
        <div class="alert alert-warning">
            {{ __('No milestones found in your learning plan.') }}
        </div>
    @endif
    
    @if(isset($plan->next_recommended_quiz) && $plan->next_recommended_quiz)
        <div class="next-action">
            <h3>{{ __('Recommended Next Step') }}</h3>
            <a href="{{ route('quizzes.start', $plan->next_recommended_quiz->id) }}" class="btn btn-success">
                {{ __('Start') }}: {{ $plan->next_recommended_quiz->title }}
            </a>
        </div>
    @endif
</div>