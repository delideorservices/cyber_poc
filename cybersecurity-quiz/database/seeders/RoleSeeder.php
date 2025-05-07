<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Role;
use App\Models\Sector;

class RoleSeeder extends Seeder
{
    public function run()
    {
        // Banking sector roles
        $bankingSector = Sector::where('name', 'Banking')->first();
        $bankingRoles = [
            ['name' => 'Bank Teller', 'description' => 'Handles customer transactions and basic banking services'],
            ['name' => 'Loan Officer', 'description' => 'Reviews and processes loan applications'],
            ['name' => 'Bank Manager', 'description' => 'Oversees branch operations and staff'],
            ['name' => 'IT Security Specialist', 'description' => 'Maintains security of banking systems']
        ];

        foreach ($bankingRoles as $role) {
            Role::create([
                'sector_id' => $bankingSector->id,
                'name' => $role['name'],
                'description' => $role['description']
            ]);
        }

        // Travel sector roles
        $travelSector = Sector::where('name', 'Travel')->first();
        $travelRoles = [
            ['name' => 'Travel Agent', 'description' => 'Arranges travel services for customers'],
            ['name' => 'Hotel Staff', 'description' => 'Works in hospitality and accommodation services'],
            ['name' => 'Airline Employee', 'description' => 'Works for an airline in various capacities'],
            ['name' => 'Tour Guide', 'description' => 'Conducts tours and provides information']
        ];

        foreach ($travelRoles as $role) {
            Role::create([
                'sector_id' => $travelSector->id,
                'name' => $role['name'],
                'description' => $role['description']
            ]);
        }

        // Healthcare sector roles
        $healthcareSector = Sector::where('name', 'Healthcare')->first();
        $healthcareRoles = [
            ['name' => 'Doctor', 'description' => 'Medical professional who diagnoses and treats patients'],
            ['name' => 'Nurse', 'description' => 'Provides patient care and assistance'],
            ['name' => 'Medical Administrator', 'description' => 'Manages healthcare facility operations'],
            ['name' => 'Lab Technician', 'description' => 'Conducts laboratory tests and analyses']
        ];

        foreach ($healthcareRoles as $role) {
            Role::create([
                'sector_id' => $healthcareSector->id,
                'name' => $role['name'],
                'description' => $role['description']
            ]);
        }

        // Finance sector roles
        $financeSector = Sector::where('name', 'Finance')->first();
        $financeRoles = [
            ['name' => 'Financial Advisor', 'description' => 'Provides financial guidance and planning'],
            ['name' => 'Investment Analyst', 'description' => 'Analyzes market trends and investment opportunities'],
            ['name' => 'Accountant', 'description' => 'Manages financial records and reporting'],
            ['name' => 'Compliance Officer', 'description' => 'Ensures regulatory compliance']
        ];

        foreach ($financeRoles as $role) {
            Role::create([
                'sector_id' => $financeSector->id,
                'name' => $role['name'],
                'description' => $role['description']
            ]);
        }
    }
}