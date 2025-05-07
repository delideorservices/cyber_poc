<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateQuizzesTable extends Migration
{
    public function up()
    {
        Schema::create('quizzes', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->text('description')->nullable();
            $table->foreignId('user_id')->constrained(); // User the quiz was created for
            $table->foreignId('topic_id')->constrained(); // Primary topic
            $table->foreignId('sector_id')->nullable()->constrained(); // Sector-specific content
            $table->foreignId('role_id')->nullable()->constrained(); // Role-specific content
            $table->integer('difficulty_level')->default(1); // 1-5 scale
            $table->json('metadata')->nullable(); // Store any additional quiz data
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('quizzes');
    }
}