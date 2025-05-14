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
use App\Http\Controllers\LearningPlanController;
use App\Http\Controllers\AnalyticsController;
use App\Http\Controllers\SkillImprovementController;
use App\Http\Controllers\RecommendationController;

// Public routes
Route::post('/login', [LoginController::class, 'login']);
Route::post('/register', [RegisterController::class, 'register']);

// Reference data (public)
Route::get('/sectors', [SectorController::class, 'index']);
Route::get('/roles', [RoleController::class, 'index']);
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

    // Direct Agent API routes
    Route::prefix('agent')->group(function () {
        Route::post('/execute/{agentName}', [AgentController::class, 'executeAgent']);
        Route::get('/test/{agentName}', [AgentController::class, 'testAgent']);
    });

    // Learning Plan routes
    Route::prefix('learning-plan')->group(function () {
        Route::get('/', [LearningPlanController::class, 'index']);
        Route::post('/generate', [LearningPlanController::class, 'generate']);
        Route::get('/{id}/modules', [LearningPlanController::class, 'getModules']);
        Route::post('/module/{id}/start', [LearningPlanController::class, 'startModule']);
        Route::post('/module/{id}/progress', [LearningPlanController::class, 'updateProgress']);
        Route::post('/module/{id}/complete', [LearningPlanController::class, 'completeModule']);
    });

    // Analytics routes
    Route::prefix('analytics')->group(function () {
        Route::get('/user', [AnalyticsController::class, 'getUserAnalytics']);
        Route::get('/skill/{id}', [AnalyticsController::class, 'getSkillAnalytics']);
        Route::get('/peer-comparison', [AnalyticsController::class, 'getPeerComparison']);
        Route::get('/export', [AnalyticsController::class, 'exportAnalytics']);
    });

    // Skill Improvement routes
    Route::prefix('skill-improvement')->group(function () {
        Route::get('/{id}', [SkillImprovementController::class, 'getSkillImprovement']);
        Route::post('/{id}/practice/start', [SkillImprovementController::class, 'startPracticeSession']);
        Route::post('/practice/{id}/response', [SkillImprovementController::class, 'submitPracticeResponse']);
        Route::post('/practice/{id}/complete', [SkillImprovementController::class, 'completePracticeSession']);
        Route::get('/spaced-repetition/due', [SkillImprovementController::class, 'getDueRepetitions']);
        Route::post('/spaced-repetition/{id}/complete', [SkillImprovementController::class, 'completeRepetition']);
    });

    // Recommendation routes
    Route::prefix('recommendations')->group(function () {
        Route::get('/', [RecommendationController::class, 'getRecommendations']);
        Route::get('/saved', [RecommendationController::class, 'getSavedRecommendations']);
        Route::post('/{id}/view', [RecommendationController::class, 'viewRecommendation']);
        Route::post('/{id}/complete', [RecommendationController::class, 'completeRecommendation']);
        Route::post('/{id}/save', [RecommendationController::class, 'saveRecommendation']);
        Route::delete('/{id}/save', [RecommendationController::class, 'removeSavedRecommendation']);
    });
});
