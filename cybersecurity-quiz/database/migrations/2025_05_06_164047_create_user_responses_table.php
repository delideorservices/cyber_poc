<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateUserResponsesTable extends Migration
{
    public function up()
    {
        Schema::create('user_responses', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained();
            $table->foreignId('question_id')->constrained();
            $table->json('response'); // User's answer
            $table->boolean('is_correct')->nullable(); // Whether response was correct
            $table->integer('points_earned')->default(0); // Points earned
            $table->timestamp('answered_at');
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('user_responses');
    }
}