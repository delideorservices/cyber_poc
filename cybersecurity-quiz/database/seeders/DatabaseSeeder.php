<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     *
     * @return void
     */
    public function run()
    {
        $this->call([
            SectorSeeder::class,
            RoleSeeder::class,
            SkillSeeder::class,
            CertificationSeeder::class,
            TopicSeeder::class,
            UserSeeder::class, // Add this line
        ]);
    }
}
