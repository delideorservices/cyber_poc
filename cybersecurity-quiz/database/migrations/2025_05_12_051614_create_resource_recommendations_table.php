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
        Schema::create('resource_recommendations', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->foreignId('resource_id')->constrained()->onDelete('cascade');
            $table->string('recommendation_reason')->nullable();
            $table->decimal('relevance_score', 5, 2)->nullable();
            $table->enum('status', ['new', 'viewed', 'completed', 'dismissed'])->default('new');
            $table->timestamp('viewed_at')->nullable();
            $table->timestamp('completed_at')->nullable();
            $table->integer('user_rating')->nullable();
            $table->text('user_feedback')->nullable();
            $table->timestamps();

            // Unique constraint to prevent duplicate recommendations
            $table->unique(['user_id', 'resource_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('resource_recommendations');
    }
};
