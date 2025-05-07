<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateQuestionsTable extends Migration
{
    public function up()
    {
        Schema::create('questions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('chapter_id')->constrained()->onDelete('cascade');
            $table->enum('type', ['mcq', 'true_false', 'fill_blank', 'drag_drop']);
            $table->text('content'); // The question text
            $table->json('options')->nullable(); // Options for MCQ/drag-drop
            $table->json('correct_answer'); // Correct answer(s)
            $table->integer('points')->default(1); // Points for this question
            $table->text('explanation')->nullable(); // Explanation of correct answer
            $table->integer('sequence')->default(1); // Order within chapter
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('questions');
    }
}