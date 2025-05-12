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
        Schema::create('skill_analytics', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->foreignId('skill_id')->constrained()->onDelete('cascade');
            $table->decimal('proficiency_score', 5, 2)->default(0); // 0-100
            $table->enum('strength_level', ['novice', 'developing', 'competent', 'proficient', 'expert'])->default('novice');
            $table->boolean('is_strength')->default(false);
            $table->boolean('is_weakness')->default(false);
            $table->decimal('benchmark_percentile', 5, 2)->nullable();
            $table->decimal('improvement_rate', 5, 2)->nullable();
            $table->timestamp('last_assessment_date')->nullable();
            $table->integer('assessment_count')->default(0);
            $table->json('historical_scores')->nullable();
            $table->text('gap_analysis')->nullable();
            $table->timestamps();

            // Unique constraint to prevent duplicate analytics entries
            $table->unique(['user_id', 'skill_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('skill_analytics');
    }
};
