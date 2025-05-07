<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateCertificationsTable extends Migration
{
    public function up()
    {
        Schema::create('certifications', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('provider')->nullable();
            $table->text('description')->nullable();
            $table->timestamps();
        });
        
        // Insert common cybersecurity certifications
        DB::table('certifications')->insert([
            ['name' => 'CompTIA Security+', 'provider' => 'CompTIA', 'description' => 'Foundational IT security certification', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Certified Information Systems Security Professional (CISSP)', 'provider' => 'ISC2', 'description' => 'Advanced security certification', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Certified Ethical Hacker (CEH)', 'provider' => 'EC-Council', 'description' => 'Ethical hacking certification', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Certified Information Security Manager (CISM)', 'provider' => 'ISACA', 'description' => 'Security management certification', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Certified Cloud Security Professional (CCSP)', 'provider' => 'ISC2', 'description' => 'Cloud security certification', 'created_at' => now(), 'updated_at' => now()],
        ]);
    }

    public function down()
    {
        Schema::dropIfExists('certifications');
    }
}