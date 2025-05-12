<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Auth\LoginController;
use App\Http\Controllers\Auth\RegisterController;
use App\Http\Controllers\SectorController;
use App\Http\Controllers\RoleController;
use App\Http\Controllers\SkillController;
use App\Http\Controllers\CertificationController;
use App\Http\Controllers\TopicController;
use App\Http\Controllers\UserProfileController;
use App\Http\Controllers\QuizController;
use App\Http\Controllers\QuizResultController;

// Public routes
Route::post('/login', [LoginController::class, 'login']);
Route::post('/register', [RegisterController::class, 'register']);

// Reference data (public)
Route::get('/sectors', [SectorController::class, 'index']);
Route::get('/roles', [RoleController::class, 'index']);

// Protected routes
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/user', function (Request $request) {
        return $request->user();
    });
    
    // User profile
    Route::get('/profile', [UserProfileController::class, 'show']);
    Route::put('/profile', [UserProfileController::class, 'update']);
    
    // Skills
    Route::get('/skills', [SkillController::class, 'index']);
    Route::get('/skills/{skill}', [SkillController::class, 'show']);
    Route::put('/profile/skills', [UserProfileController::class, 'addSkill']);
    Route::delete('/profile/skills/{skill}', [UserProfileController::class, 'removeSkill']);
    
    // Certifications
    Route::get('/certifications', [CertificationController::class, 'index']);
    Route::get('/certifications/{certification}', [CertificationController::class, 'show']);
    Route::put('/profile/certifications', [UserProfileController::class, 'addCertification']);
    Route::delete('/profile/certifications/{certification}', [UserProfileController::class, 'removeCertification']);
    
    // Password updates
    Route::put('/password', [UserProfileController::class, 'updatePassword']);
    
    // Topics
    Route::get('/topics', [TopicController::class, 'index']);
    Route::get('/topics/{topic}', [TopicController::class, 'show']);
    
    // Quizzes
    Route::get('/quizzes', [QuizController::class, 'index']);
    Route::get('/quizzes/{quiz}', [QuizController::class, 'show']);
    Route::post('/quizzes/generate', [QuizController::class, 'generate']);
    Route::post('/quizzes/{quiz}/submit', [QuizController::class, 'submit']);
    
    // Quiz results
    Route::get('/results', [QuizResultController::class, 'index']);
    Route::get('/results/{result}', [QuizResultController::class, 'show']);
});
Route::middleware(['auth:sanctum'])->prefix('analytics')->group(function () {
    Route::post('/enhanced', [AnalyticsController::class, 'getEnhancedAnalysis']);
    Route::get('/skills/{userId}', [AnalyticsController::class, 'getSkillPerformance']);
    Route::get('/peer-comparison/{userId}', [AnalyticsController::class, 'getPeerComparison']);
});
// Learning Plan routes
Route::get('users/{userId}/learning-plan', 'LearningPlanController@getUserPlan');
Route::patch('users/{userId}/learning-plan/milestones/{milestoneId}', 'LearningPlanController@updateMilestone');

// Analytics routes
Route::get('users/{userId}/analytics', 'AnalyticsController@getUserAnalytics');
Route::get('users/{userId}/skills/{skillId}/improvement', 'AnalyticsController@getSkillImprovementActivities');

// Practice routes
Route::post('users/{userId}/skills/{skillId}/practice', 'PracticeController@startPractice');
Route::get('practice-sessions/{sessionId}', 'PracticeController@getSessionData');
Route::post('users/{userId}/practice-sessions/{sessionId}', 'PracticeController@savePracticeResults');

// Recommendation routes
Route::get('users/{userId}/recommendations', 'RecommendationController@getUserRecommendations');
Route::post('users/{userId}/recommendations/{recommendationId}/interaction', 'RecommendationController@recordInteraction');
