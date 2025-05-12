<!-- Improvement Areas Partial -->
<div class="improvements-container">
    <div class="card">
        <div class="card-header bg-warning">
            <h4>{{ __('Areas for Improvement') }}</h4>
        </div>
        <div class="card-body">
            @if(isset($improvements) && count($improvements) > 0)
                <ul class="list-group">
                    @foreach($improvements as $improvement)
                        <li class="list-group-item">
                            <div class="improvement-item">
                                <h5>{{ $improvement->name }}</h5>
                                <p>{{ $improvement->description }}</p>
                                @if(isset($improvement->score))
                                    <div class="improvement-score">
                                        <span class="badge badge-warning">{{ $improvement->score }}%</span>
                                    </div>
                                @endif
                                
                                @if(isset($improvement->recommendation_url) && $improvement->recommendation_url)
                                    <div class="improvement-action mt-2">
                                        <a href="{{ $improvement->recommendation_url }}" class="btn btn-sm btn-outline-warning">
                                            {{ __('Improve This Skill') }}
                                        </a>
                                    </div>
                                @endif
                            </div>
                        </li>
                    @endforeach
                </ul>
            @else
                <p>{{ __('Complete more quizzes to identify areas for improvement.') }}</p>
            @endif
        </div>
    </div>
</div>