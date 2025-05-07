<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateUserCertificationsTable extends Migration
{
    public function up()
    {
        Schema::create('user_certifications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->foreignId('certification_id')->constrained()->onDelete('cascade');
            $table->date('obtained_date')->nullable();
            $table->date('expiry_date')->nullable();
            $table->timestamps();
            
            // Ensure user can only have each certification once
            $table->unique(['user_id', 'certification_id']);
        });
    }

    public function down()
    {
        Schema::dropIfExists('user_certifications');
    }
}