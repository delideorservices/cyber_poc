@extends('layouts.app')

@section('content')
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>{{ __('Skill Improvement Center') }}</h1>
            
            @if(isset($skillGaps) && count($skillGaps) > 0)
                <div class="skill-improvement-intro">
                    <p>{{ __('Based on your quiz results, we recommend focusing on the following skills:') }}</p>
                </div>
                
                <div class="skill-gaps-container">
                    @foreach($skillGaps as $skill)
                        @include('skill-improvement.skill-card', ['skill' => $skill])
                    @endforeach
                </div>
            @elseif(isset($allSkills) && count($allSkills) > 0)
                <div class="skill-improvement-intro">
                    <p>{{ __('Browse skills to improve your cybersecurity knowledge:') }}</p>
                </div>
                
                <div class="skills-browser">
                    @foreach($allSkills as $category => $skills)
                        <div class="skill-category">
                            <h3>{{ $category }}</h3>
                            <div class="row">
                                @foreach($skills as $skill)
                                    <div class="col-md-4 mb-4">
                                        @include('skill-improvement.skill-card', ['skill' => $skill])
                                    </div>
                                @endforeach
                            </div>
                        </div>
                    @endforeach
                </div>
            @else
                <div class="alert alert-info">
                    {{ __('Complete more quizzes to get personalized skill improvement recommendations.') }}
                </div>
                
                @if(isset($availableQuiz) && $availableQuiz)
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">{{ __('Start your skill assessment') }}</h5>
                            <p>{{ __('Take a cybersecurity quiz to identify your skill gaps.') }}</p>
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