<!-- Skill Card Template -->
<div class="skill-card" id="skill-{{ $skill->id }}">
    <div class="card">
        <div class="card-header">
            <h4>{{ $skill->name }}</h4>
            @if(isset($skill->current_level))
                <div class="skill-level">
                    <span class="badge {{ $skill->current_level >= 4 ? 'badge-success' : ($skill->current_level >= 2 ? 'badge-warning' : 'badge-danger') }}">
                        {{ __('Level') }} {{ $skill->current_level }}/5
                    </span>
                </div>
            @endif
        </div>
        <div class="card-body">
            <p>{{ $skill->description }}</p>
            
            @if(isset($skill->recommendation))
                <div class="skill-recommendation">
                    <h5>{{ __('Recommendation') }}:</h5>
                    <p>{{ $skill->recommendation }}</p>
                </div>
            @endif
            
            @if(isset($skill->practice_options) && count($skill->practice_options) > 0)
                <div class="practice-options">
                    <h5>{{ __('Practice Options') }}:</h5>
                    <div class="list-group">
                        @foreach($skill->practice_options as $option)
                            <a href="{{ $option->url }}" class="list-group-item list-group-item-action">
                                <div class="d-flex w-100 justify-content-between">
                                    <h6 class="mb-1">{{ $option->title }}</h6>
                                    @if(isset($option->difficulty))
                                        <small>
                                            {{ __('Difficulty') }}: {{ $option->difficulty }}/5
                                        </small>
                                    @endif
                                </div>
                                <p class="mb-1">{{ $option->description }}</p>
                            </a>
                        @endforeach
                    </div>
                </div>
            @endif
            
            @if(isset($skill->resource_url) && $skill->resource_url)
                <div class="skill-resources mt-3">
                    <a href="{{ $skill->resource_url }}" class="btn btn-outline-primary">
                        {{ __('View Learning Resources') }}
                    </a>
                </div>
            @endif
        </div>
    </div>
</div>