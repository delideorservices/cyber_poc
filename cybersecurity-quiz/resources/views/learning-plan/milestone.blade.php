<!-- Single Milestone Component -->
<div class="milestone {{ $milestone->is_completed ? 'completed' : '' }}" id="milestone-{{ $milestone->id }}">
    <div class="milestone-header">
        <h3>{{ $milestone->title }}</h3>
        @if($milestone->is_completed)
            <span class="badge badge-success">{{ __('Completed') }}</span>
        @else
            <span class="badge badge-secondary">{{ __('In Progress') }}</span>
        @endif
    </div>
    
    <div class="milestone-content">
        <p>{{ $milestone->description }}</p>
        
        @if(count($milestone->steps) > 0)
            <div class="milestone-steps">
                @foreach($milestone->steps as $step)
                    <div class="step {{ $step->is_completed ? 'completed' : '' }}">
                        <div class="step-indicator">
                            @if($step->is_completed)
                                <i class="fas fa-check-circle"></i>
                            @else
                                <i class="far fa-circle"></i>
                            @endif
                        </div>
                        <div class="step-content">
                            <h4>{{ $step->title }}</h4>
                            <p>{{ $step->description }}</p>
                            
                            @if(!$step->is_completed && isset($step->action_url) && $step->action_url)
                                <a href="{{ $step->action_url }}" class="btn btn-sm btn-primary">
                                    {{ $step->action_text ?? __('Start') }}
                                </a>
                            @endif
                        </div>
                    </div>
                @endforeach
            </div>
        @endif
    </div>
    
    @if(!$milestone->is_completed && isset($milestone->next_action) && $milestone->next_action)
        <div class="milestone-action">
            <a href="{{ $milestone->next_action['url'] }}" class="btn btn-primary">
                {{ $milestone->next_action['text'] }}
            </a>
        </div>
    @endif
</div>