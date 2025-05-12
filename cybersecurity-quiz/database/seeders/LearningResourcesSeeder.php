<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class LearningResourcesSeeder extends Seeder
{
    public function run()
    {
        $resources = [
            // Network Security Resources
            [
                'title' => 'Fundamentals of Network Security',
                'description' => 'A comprehensive guide to network security fundamentals for beginners',
                'resource_type' => 'article',
                'url' => 'https://cybersecurity-resources.example/network-fundamentals',
                'difficulty_level' => 1,
                'sector_id' => null, // Generic, not sector-specific
                'skill_tags' => json_encode([1]), // Network Security skill ID
                'topic_tags' => json_encode([1, 3]), // Relevant topic IDs
                'estimated_minutes' => 45,
                'is_premium' => false,
                'created_at' => Carbon::now(),
                'updated_at' => Carbon::now(),
            ],
            // Add more resource entries here...
        ];

        DB::table('learning_resources')->insert($resources);
    }
}