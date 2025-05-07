<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateRolesTable extends Migration
{
    public function up()
    {
        Schema::create('roles', function (Blueprint $table) {
            $table->id();
            $table->foreignId('sector_id')->constrained();
            $table->string('name');
            $table->text('description')->nullable();
            $table->timestamps();
        });
        
        // Insert default roles for each sector
        // Banking Roles
        DB::table('roles')->insert([
            ['sector_id' => 1, 'name' => 'Bank Teller', 'description' => 'Handles customer transactions', 'created_at' => now(), 'updated_at' => now()],
            ['sector_id' => 1, 'name' => 'Loan Officer', 'description' => 'Processes loan applications', 'created_at' => now(), 'updated_at' => now()],
            ['sector_id' => 1, 'name' => 'Bank Manager', 'description' => 'Oversees branch operations', 'created_at' => now(), 'updated_at' => now()],
        ]);
        
        // Travel Roles
        DB::table('roles')->insert([
            ['sector_id' => 2, 'name' => 'Travel Agent', 'description' => 'Books travel arrangements', 'created_at' => now(), 'updated_at' => now()],
            ['sector_id' => 2, 'name' => 'Hotel Staff', 'description' => 'Assists hotel guests', 'created_at' => now(), 'updated_at' => now()],
            ['sector_id' => 2, 'name' => 'Airline Employee', 'description' => 'Provides airline services', 'created_at' => now(), 'updated_at' => now()],
        ]);
        
        // Healthcare Roles
        DB::table('roles')->insert([
            ['sector_id' => 3, 'name' => 'Nurse', 'description' => 'Provides patient care', 'created_at' => now(), 'updated_at' => now()],
            ['sector_id' => 3, 'name' => 'Doctor', 'description' => 'Diagnoses and treats patients', 'created_at' => now(), 'updated_at' => now()],
            ['sector_id' => 3, 'name' => 'Administrator', 'description' => 'Manages healthcare operations', 'created_at' => now(), 'updated_at' => now()],
        ]);
        
        // Finance Roles
        DB::table('roles')->insert([
            ['sector_id' => 4, 'name' => 'Financial Advisor', 'description' => 'Provides financial guidance', 'created_at' => now(), 'updated_at' => now()],
            ['sector_id' => 4, 'name' => 'Accountant', 'description' => 'Manages financial records', 'created_at' => now(), 'updated_at' => now()],
            ['sector_id' => 4, 'name' => 'Investment Analyst', 'description' => 'Analyzes investment opportunities', 'created_at' => now(), 'updated_at' => now()],
        ]);
    }

    public function down()
    {
        Schema::dropIfExists('roles');
    }
}