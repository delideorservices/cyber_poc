<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateUserQuizResultsTable extends Migration
{
    public function up()
    {
        Schema::create('user_quiz_results', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained();
            $table->foreignId('quiz_id')->constrained();
            $table->integer('total_points')->default(0);
            $table->integer('points_earned')->default(0);
            $table->decimal('percentage_score', 5, 2)->default(0);
            $table->json('chapter_scores')->nullable(); // Scores by chapter
            $table->json('skill_gaps')->nullable(); // Identified skill gaps
            $table->text('feedback')->nullable(); // Generated feedback
            $table->timestamp('completed_at')->nullable();
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('user_quiz_results');
    }
}