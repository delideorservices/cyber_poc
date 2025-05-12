<!-- Recommendation Item Card -->
<div class="recommendation-item" id="recommendation-{{ $item->id }}">
    <div class="card mb-3">
        <div class="card-body">
            <h4 class="card-title">{{ $item->title }}</h4>
            
            @if(isset($item->type) && $item->type)
                <div class="recommendation-type">
                    <span class="badge badge-info">{{ $item->type_label }}</span>
                    
                    @if(isset($item->difficulty))
                        <span class="badge badge-secondary">
                            {{ __('Difficulty') }}: {{ $item->difficulty }}/5
                        </span>
                    @endif
                </div>
            @endif
            
            <p class="card-text mt-2">{{ $item->description }}</p>
            
            @if(isset($item->reason) && $item->reason)
                <div class="recommendation-reason">
                    <h5>{{ __('Why this is recommended for you') }}:</h5>
                    <p>{{ $item->reason }}</p>
                </div>
            @endif
            
            @if(isset($item->skills) && count($item->skills) > 0)
                <div class="recommendation-skills">
                    <h5>{{ __('Skills covered') }}:</h5>
                    <div class="skill-tags">
                        @foreach($item->skills as $skill)
                            <span class="badge badge-light">{{ $skill->name }}</span>
                        @endforeach
                    </div>
                </div>
            @endif
            
            <div class="recommendation-actions mt-3">
                @if(isset($item->url) && $item->url)
                    <a href="{{ $item->url }}" class="btn btn-primary mr-2">
                        @if($item->type == 'quiz')
                            {{ __('Start Quiz') }}
                        @elseif($item->type == 'resource')
                            {{ __('View Resource') }}
                        @elseif($item->type == 'course')
                            {{ __('Start Course') }}
                        @else
                            {{ __('View Details') }}
                        @endif
                    </a>
                @endif
                
                <button type="button" class="btn btn-outline-secondary save-for-later"
                       data-recommendation-id="{{ $item->id }}">
                    {{ __('Save for Later') }}
                </button>
            </div>
        </div>
    </div>
</div>