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
        Schema::create('resources', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->text('description')->nullable();
            $table->enum('resource_type', ['article', 'video', 'course', 'tool', 'reference']);
            $table->string('url')->nullable();
            $table->text('content')->nullable();
            $table->string('author')->nullable();
            $table->integer('difficulty_level')->default(1); // 1-5 scale
            $table->integer('estimated_time_minutes')->nullable();
            $table->json('tags')->nullable();
            $table->json('related_skills')->nullable();
            $table->json('related_topics')->nullable();
            $table->enum('publish_status', ['draft', 'published', 'archived'])->default('published');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('resources');
    }
};
