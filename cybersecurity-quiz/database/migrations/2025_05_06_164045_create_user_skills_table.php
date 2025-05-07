<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateUserSkillsTable extends Migration
{
    public function up()
    {
        Schema::create('user_skills', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->foreignId('skill_id')->constrained()->onDelete('cascade');
            $table->integer('proficiency_level')->default(1); // 1-5 scale
            $table->timestamps();
            
            // Ensure user can only have each skill once
            $table->unique(['user_id', 'skill_id']);
        });
    }

    public function down()
    {
        Schema::dropIfExists('user_skills');
    }
}