<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Sector;

class SectorSeeder extends Seeder
{
    public function run()
    {
        $sectors = [
            ['name' => 'Banking', 'description' => 'Financial institutions and banking services'],
            ['name' => 'Travel', 'description' => 'Travel, tourism, and hospitality services'],
            ['name' => 'Healthcare', 'description' => 'Healthcare providers and medical services'],
            ['name' => 'Finance', 'description' => 'Financial services and investment organizations']
        ];

        foreach ($sectors as $sector) {
            Sector::create($sector);
        }
    }
}