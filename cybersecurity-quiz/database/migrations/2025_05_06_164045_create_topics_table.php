<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateTopicsTable extends Migration
{
    public function up()
    {
        Schema::create('topics', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->text('description')->nullable();
            $table->foreignId('sector_id')->nullable()->constrained(); // Topic can be sector-specific
            $table->json('keywords')->nullable(); // Store related keywords as JSON
            $table->timestamps();
        });
        
        // Insert default cybersecurity topics
        DB::table('topics')->insert([
            [
                'name' => 'Phishing Attacks', 
                'description' => 'Email and social engineering attacks', 
                'keywords' => json_encode(['email security', 'social engineering', 'malicious links']),
                'created_at' => now(), 
                'updated_at' => now()
            ],
            [
                'name' => 'Password Security', 
                'description' => 'Password best practices', 
                'keywords' => json_encode(['strong passwords', 'multi-factor authentication', 'password managers']),
                'created_at' => now(), 
                'updated_at' => now()
            ],
            [
                'name' => 'Data Protection', 
                'description' => 'Protecting sensitive data', 
                'keywords' => json_encode(['encryption', 'data classification', 'data handling']),
                'created_at' => now(), 
                'updated_at' => now()
            ],
            [
                'name' => 'Mobile Security', 
                'description' => 'Securing mobile devices', 
                'keywords' => json_encode(['device security', 'mobile apps', 'BYOD']),
                'created_at' => now(), 
                'updated_at' => now()
            ],
        ]);
        
        // Banking-specific topics
        DB::table('topics')->insert([
            [
                'name' => 'Financial Fraud Prevention', 
                'description' => 'Preventing financial fraud', 
                'sector_id' => 1,
                'keywords' => json_encode(['fraud detection', 'transaction monitoring', 'customer verification']),
                'created_at' => now(), 
                'updated_at' => now()
            ],
        ]);
        
        // Healthcare-specific topics
        DB::table('topics')->insert([
            [
                'name' => 'Patient Data Privacy', 
                'description' => 'Protecting patient information', 
                'sector_id' => 3,
                'keywords' => json_encode(['HIPAA', 'medical records', 'health information']),
                'created_at' => now(), 
                'updated_at' => now()
            ],
        ]);
    }

    public function down()
    {
        Schema::dropIfExists('topics');
    }
}