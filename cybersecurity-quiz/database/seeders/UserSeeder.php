<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\User;
use App\Models\Sector;
use App\Models\Role;
use App\Models\Skill;
use App\Models\Certification;
use Illuminate\Support\Facades\Hash;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        // Get the sectors
        $bankingSector = Sector::where('name', 'Banking')->first();
        $travelSector = Sector::where('name', 'Travel')->first();
        $healthcareSector = Sector::where('name', 'Healthcare')->first();
        $financeSector = Sector::where('name', 'Finance')->first();
        
        // Create a Banking sector user
        $bankingUser = User::create([
            'name' => 'John Banking',
            'email' => 'banking@example.com',
            'password' => Hash::make('password123'),
            'gender' => 'male',
            'age' => 35,
            'sector_id' => $bankingSector->id,
            'role_id' => Role::where('sector_id', $bankingSector->id)->first()->id,
            'years_experience' => 8,
            'learning_goal' => 'Improve knowledge of financial cybersecurity threats',
            'preferred_language' => 'en',
            'email_verified_at' => now(),
        ]);
        
        // Assign skills and certifications to Banking user
        $bankingUser->skills()->attach([
            Skill::where('name', 'Network Security')->first()->id => ['proficiency_level' => 4],
            Skill::where('name', 'Phishing Awareness')->first()->id => ['proficiency_level' => 5],
            Skill::where('name', 'Data Protection')->first()->id => ['proficiency_level' => 3],
        ]);
        
        $bankingUser->certifications()->attach([
            Certification::where('name', 'CompTIA Security+')->first()->id => [
                'obtained_date' => now()->subYears(2),
                'expiry_date' => now()->addYears(1),
            ],
        ]);
        
        // Create a Travel sector user
        $travelUser = User::create([
            'name' => 'Sarah Travel',
            'email' => 'travel@example.com',
            'password' => Hash::make('password123'),
            'gender' => 'female',
            'age' => 29,
            'sector_id' => $travelSector->id,
            'role_id' => Role::where('sector_id', $travelSector->id)->first()->id,
            'years_experience' => 5,
            'learning_goal' => 'Understand security risks in travel booking systems',
            'preferred_language' => 'en',
            'email_verified_at' => now(),
        ]);
        
        // Assign skills and certifications to Travel user
        $travelUser->skills()->attach([
            Skill::where('name', 'Password Management')->first()->id => ['proficiency_level' => 3],
            Skill::where('name', 'Mobile Security')->first()->id => ['proficiency_level' => 4],
        ]);
        
        $travelUser->certifications()->attach([
            Certification::where('name', 'Certified Information Systems Security Professional (CISSP)')->first()->id => [
                'obtained_date' => now()->subMonths(8),
                'expiry_date' => now()->addYears(2),
            ],
        ]);
        
        // Create a Healthcare sector user
        $healthcareUser = User::create([
            'name' => 'Michael Healthcare',
            'email' => 'healthcare@example.com',
            'password' => Hash::make('password123'),
            'gender' => 'male',
            'age' => 42,
            'sector_id' => $healthcareSector->id,
            'role_id' => Role::where('sector_id', $healthcareSector->id)->first()->id,
            'years_experience' => 12,
            'learning_goal' => 'Strengthen patient data protection strategies',
            'preferred_language' => 'en',
            'email_verified_at' => now(),
        ]);
        
        // Assign skills and certifications to Healthcare user
        $healthcareUser->skills()->attach([
            Skill::where('name', 'Data Protection')->first()->id => ['proficiency_level' => 5],
            Skill::where('name', 'Security Compliance')->first()->id => ['proficiency_level' => 4],
            Skill::where('name', 'Encryption')->first()->id => ['proficiency_level' => 3],
        ]);
        
        $healthcareUser->certifications()->attach([
            Certification::where('name', 'Certified Information Privacy Professional (CIPP)')->first()->id => [
                'obtained_date' => now()->subYears(1),
                'expiry_date' => now()->addYears(2),
            ],
        ]);
        
        // Create a Finance sector user
        $financeUser = User::create([
            'name' => 'Emily Finance',
            'email' => 'finance@example.com',
            'password' => Hash::make('password123'),
            'gender' => 'female',
            'age' => 38,
            'sector_id' => $financeSector->id,
            'role_id' => Role::where('sector_id', $financeSector->id)->first()->id,
            'years_experience' => 10,
            'learning_goal' => 'Master investment fraud detection techniques',
            'preferred_language' => 'en',
            'email_verified_at' => now(),
        ]);
        
        // Assign skills and certifications to Finance user
        $financeUser->skills()->attach([
            Skill::where('name', 'Phishing Awareness')->first()->id => ['proficiency_level' => 5],
            Skill::where('name', 'Security Compliance')->first()->id => ['proficiency_level' => 5],
            Skill::where('name', 'Social Engineering Defense')->first()->id => ['proficiency_level' => 4],
        ]);
        
        $financeUser->certifications()->attach([
            Certification::where('name', 'Certified Information Security Manager (CISM)')->first()->id => [
                'obtained_date' => now()->subYears(3),
                'expiry_date' => now()->addMonths(6),
            ],
            Certification::where('name', 'Certified Ethical Hacker (CEH)')->first()->id => [
                'obtained_date' => now()->subYears(1),
                'expiry_date' => now()->addYears(2),
            ],
        ]);
    }
}

