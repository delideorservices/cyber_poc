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
        Schema::create('learning_plan_modules', function (Blueprint $table) {
            $table->id();
            $table->foreignId('learning_plan_id')->constrained()->onDelete('cascade');
            $table->string('title');
            $table->text('description')->nullable();
            $table->foreignId('skill_id')->nullable()->constrained()->onDelete('set null');
            $table->foreignId('topic_id')->nullable()->constrained()->onDelete('set null');
            $table->integer('sequence')->default(1);
            $table->decimal('estimated_hours', 5, 2)->nullable();
            $table->enum('module_type', ['quiz', 'practice', 'resource', 'assessment']);
            $table->bigInteger('content_reference_id')->nullable();
            $table->json('prerequisites')->nullable();
            $table->enum('status', ['not_started', 'in_progress', 'completed'])->default('not_started');
            $table->integer('difficulty_level')->default(1); // 1-5 scale
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('learning_plan_modules');
    }
};
