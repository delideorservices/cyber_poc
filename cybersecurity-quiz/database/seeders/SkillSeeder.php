<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Skill;

class SkillSeeder extends Seeder
{
    public function run()
    {
        $skills = [
            ['name' => 'Network Security', 'description' => 'Knowledge of securing network infrastructure'],
            ['name' => 'Password Management', 'description' => 'Understanding of secure password practices'],
            ['name' => 'Phishing Awareness', 'description' => 'Ability to identify and avoid phishing attempts'],
            ['name' => 'Data Protection', 'description' => 'Knowledge of safeguarding sensitive information'],
            ['name' => 'Mobile Security', 'description' => 'Understanding of securing mobile devices'],
            ['name' => 'Encryption', 'description' => 'Knowledge of data encryption techniques'],
            ['name' => 'Incident Response', 'description' => 'Ability to respond to security incidents'],
            ['name' => 'Security Compliance', 'description' => 'Understanding of regulatory requirements'],
            ['name' => 'Cloud Security', 'description' => 'Knowledge of securing cloud environments'],
            ['name' => 'Social Engineering Defense', 'description' => 'Ability to recognize manipulation tactics']
        ];

        foreach ($skills as $skill) {
            Skill::create($skill);
        }
    }
}
