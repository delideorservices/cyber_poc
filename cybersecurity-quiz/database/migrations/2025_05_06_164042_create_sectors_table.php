<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateSectorsTable extends Migration
{
    public function up()
    {
        Schema::create('sectors', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->text('description')->nullable();
            $table->timestamps();
        });
        
        // Insert default sectors
        DB::table('sectors')->insert([
            ['name' => 'Banking', 'description' => 'Financial institutions', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Travel', 'description' => 'Travel and hospitality', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Healthcare', 'description' => 'Healthcare providers', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'Finance', 'description' => 'Financial services', 'created_at' => now(), 'updated_at' => now()],
        ]);
    }

    public function down()
    {
        Schema::dropIfExists('sectors');
    }
}