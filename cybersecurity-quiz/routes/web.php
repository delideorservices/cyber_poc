<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\HomeController;

// Redirect all routes to SPA entry point
Route::get('/{any?}', function () {
    return view('app');
})->where('any', '^(?!api).*$');
Route::middleware(['auth'])->prefix('analytics')->name('analytics.')->group(function () {
    Route::get('/', [AnalyticsController::class, 'dashboard'])->name('dashboard');
    Route::get('/quiz/{quizResultId}', [AnalyticsController::class, 'quizAnalytics'])->name('quiz');
    Route::get('/skills', [AnalyticsController::class, 'skillAnalytics'])->name('skills');
});
Route::middleware(['auth'])->group(function () {
    // Skill improvement routes
    Route::prefix('skills')->group(function () {
        Route::get('/improvement', 'SkillImprovementController@index')->name('skills.improvement');
        Route::get('/improvement/session/{id}', 'SkillImprovementController@showSession')->name('skills.improvement.session');
        Route::post('/improvement/start', 'SkillImprovementController@startSession')->name('skills.improvement.start');
        Route::post('/improvement/retry/{questionId}', 'SkillImprovementController@retryQuestion')->name('skills.improvement.retry');
        Route::get('/improvement/progress', 'SkillImprovementController@progress')->name('skills.improvement.progress');
    });
});
Route::middleware(['auth'])->group(function () {
    // Spaced repetition routes
    Route::prefix('repetition')->group(function () {
        Route::get('/', 'SpacedRepetitionController@index')->name('spaced-repetition.index');
        Route::get('/session/{id}', 'SpacedRepetitionController@showSession')->name('spaced-repetition.session');
        Route::post('/session/{id}/complete', 'SpacedRepetitionController@completeSession')->name('spaced-repetition.complete');
    });
});
Route::prefix('recommendations')->group(function () {
    Route::get('/', [RecommendationController::class, 'index'])->name('recommendations.index');
    Route::post('/generate', [RecommendationController::class, 'generate'])->name('recommendations.generate');
    Route::post('/{id}/viewed', [RecommendationController::class, 'markViewed'])->name('recommendations.viewed');
    Route::post('/{id}/completed', [RecommendationController::class, 'markCompleted'])->name('recommendations.completed');
});
// Learning Plan routes
Route::get('learning-plan', 'LearningPlanController@index')->middleware('auth');

// Analytics routes
Route::get('analytics', 'AnalyticsController@index')->middleware('auth');

// Practice routes
Route::get('practice/{sessionId}', 'PracticeController@show')->middleware('auth');
Route::get('practice/{sessionId}/results', 'PracticeController@showResults')->middleware('auth');

// Recommendation routes
Route::get('recommendations', 'RecommendationController@index')->middleware('auth');