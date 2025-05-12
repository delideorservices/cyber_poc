<!-- Strengths Analysis Partial -->
<div class="strengths-container">
    <div class="card">
        <div class="card-header bg-success text-white">
            <h4>{{ __('Your Strengths') }}</h4>
        </div>
        <div class="card-body">
            @if(isset($strengths) && count($strengths) > 0)
                <ul class="list-group">
                    @foreach($strengths as $strength)
                        <li class="list-group-item">
                            <div class="strength-item">
                                <h5>{{ $strength->name }}</h5>
                                <p>{{ $strength->description }}</p>
                                @if(isset($strength->score))
                                    <div class="strength-score">
                                        <span class="badge badge-success">{{ $strength->score }}%</span>
                                    </div>
                                @endif
                            </div>
                        </li>
                    @endforeach
                </ul>
            @else
                <p>{{ __('Complete more quizzes to identify your strengths.') }}</p>
            @endif
        </div>
    </div>
</div>