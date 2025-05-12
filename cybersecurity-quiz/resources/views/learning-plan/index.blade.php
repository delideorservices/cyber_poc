@extends('layouts.app')

@section('content')
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>{{ __('Your Learning Plan') }}</h1>
            
            @if($learningPlan)
                @include('learning-plan.plan-content', ['plan' => $learningPlan])
            @else
                <div class="alert alert-info">
                    {{ __('Your personalized learning plan is being created. Please check back soon.') }}
                </div>
                
                @if(isset($pendingQuiz) && $pendingQuiz)
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">{{ __('Complete your assessment') }}</h5>
                            <p>{{ __('Taking a cybersecurity assessment will help us create a more personalized learning plan for you.') }}</p>
                            <a href="{{ route('quizzes.start', $pendingQuiz->id) }}" class="btn btn-primary">{{ __('Start Assessment') }}</a>
                        </div>
                    </div>
                @endif
            @endif
        </div>
    </div>
</div>
@endsection