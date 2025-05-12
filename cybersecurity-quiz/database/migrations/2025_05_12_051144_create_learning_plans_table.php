<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('learning_plans', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('title');
            $table->text('description')->nullable();
            $table->json('focus_areas')->nullable();
            $table->timestamp('target_completion_date')->nullable();
            $table->enum('status', ['active', 'completed', 'archived'])->default('active');
            $table->integer('difficulty_level')->default(1); // 1-5 scale
            $table->decimal('overall_progress', 5, 2)->default(0); // 0-100
            $table->json('metadata')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('learning_plans');
    }
};
