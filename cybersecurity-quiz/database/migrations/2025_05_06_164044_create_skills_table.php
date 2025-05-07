<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateSkillsTable extends Migration
{
    public function up()
    {
        Schema::create('skills', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->text('description')->nullable();
            $table->timestamps();
        });
        
        // Insert common cybersecurity skills
        DB::table('skills')->insert([
            ['name' => 'Network Security', 'description' => 'Protecting network infrastructure', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Encryption', 'description' => 'Data encryption techniques', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Threat Analysis', 'description' => 'Identifying and analyzing threats', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Incident Response', 'description' => 'Responding to security incidents', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Compliance', 'description' => 'Regulatory compliance knowledge', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Authentication Systems', 'description' => 'User authentication methods', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Penetration Testing', 'description' => 'Testing for security vulnerabilities', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Security Awareness', 'description' => 'General security best practices', 'created_at' => now(), 'updated_at' => now()],
        ]);
    }

    public function down()
    {
        Schema::dropIfExists('skills');
    }
}