<!-- Domain Proficiency Card Template -->
<div class="domain-card" id="domain-{{ $domain->id }}">
    <div class="card mb-3">
        <div class="card-header">
            <h4>{{ $domain->name }}</h4>
        </div>
        <div class="card-body">
            <div class="domain-score">
                <div class="progress">
                    <div class="progress-bar" role="progressbar" 
                         style="width: {{ $domain->percentage }}%"
                         aria-valuenow="{{ $domain->percentage }}" 
                         aria-valuemin="0" aria-valuemax="100">
                        {{ $domain->percentage }}%
                    </div>
                </div>
                <div class="score-label mt-2">
                    {{ __('Proficiency Level') }}: {{ $domain->level_label }}
                </div>
            </div>
            
            @if(isset($domain->topic_scores) && count($domain->topic_scores) > 0)
                <div class="topic-scores mt-3">
                    <h5>{{ __('Topics') }}</h5>
                    <ul class="list-group">
                        @foreach($domain->topic_scores as $topic)
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                {{ $topic->name }}
                                <span class="badge {{ $topic->percentage >= 70 ? 'badge-success' : ($topic->percentage >= 40 ? 'badge-warning' : 'badge-danger') }} badge-pill">
                                    {{ $topic->percentage }}%
                                </span>
                            </li>
                        @endforeach
                    </ul>
                </div>
            @endif
            
            @if(isset($domain->improvement_url) && $domain->improvement_url)
                <div class="domain-action mt-3">
                    <a href="{{ $domain->improvement_url }}" class="btn btn-outline-primary btn-sm">
                        {{ __('Improve This Skill') }}
                    </a>
                </div>
            @endif
        </div>
    </div>
</div>