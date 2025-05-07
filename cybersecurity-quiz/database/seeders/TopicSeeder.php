<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Topic;
use App\Models\Sector;

class TopicSeeder extends Seeder
{
    public function run()
    {
        // General topics (not sector-specific)
        $generalTopics = [
            [
                'name' => 'Phishing Prevention',
                'description' => 'Recognizing and avoiding phishing attempts',
                'keywords' => ['email security', 'phishing', 'social engineering', 'suspicious links']
            ],
            [
                'name' => 'Password Security',
                'description' => 'Best practices for secure password management',
                'keywords' => ['strong passwords', 'password managers', 'multi-factor authentication']
            ],
            [
                'name' => 'Social Engineering Defense',
                'description' => 'Protecting against manipulation tactics',
                'keywords' => ['manipulation', 'impersonation', 'pretexting', 'baiting']
            ],
            [
                'name' => 'Mobile Device Security',
                'description' => 'Securing smartphones and tablets',
                'keywords' => ['mobile security', 'device encryption', 'app permissions', 'public wifi']
            ],
            [
                'name' => 'Safe Internet Browsing',
                'description' => 'Protecting yourself while browsing the web',
                'keywords' => ['browser security', 'https', 'malicious websites', 'downloads']
            ]
        ];

        foreach ($generalTopics as $topic) {
            Topic::create([
                'name' => $topic['name'],
                'description' => $topic['description'],
                'keywords' => json_encode($topic['keywords'])
            ]);
        }

        // Banking sector topics
        $bankingSector = Sector::where('name', 'Banking')->first();
        $bankingTopics = [
            [
                'name' => 'Financial Fraud Prevention',
                'description' => 'Recognizing and preventing financial fraud',
                'keywords' => ['fraud detection', 'transaction verification', 'customer authentication']
            ],
            [
                'name' => 'Customer Data Protection',
                'description' => 'Safeguarding sensitive customer financial information',
                'keywords' => ['financial data', 'confidentiality', 'data handling']
            ],
            [
                'name' => 'ATM Security',
                'description' => 'Security measures for ATM transactions',
                'keywords' => ['card skimming', 'pin protection', 'physical security']
            ]
        ];

        foreach ($bankingTopics as $topic) {
            Topic::create([
                'name' => $topic['name'],
                'description' => $topic['description'],
                'keywords' => json_encode($topic['keywords']),
                'sector_id' => $bankingSector->id
            ]);
        }

        // Healthcare sector topics
        $healthcareSector = Sector::where('name', 'Healthcare')->first();
        $healthcareTopics = [
            [
                'name' => 'Patient Data Privacy',
                'description' => 'Protecting sensitive patient health information',
                'keywords' => ['HIPAA', 'medical records', 'confidentiality']
            ],
            [
                'name' => 'Medical Device Security',
                'description' => 'Securing connected medical devices',
                'keywords' => ['IoT security', 'device vulnerabilities', 'patient safety']
            ],
            [
                'name' => 'Healthcare Compliance',
                'description' => 'Meeting regulatory security requirements in healthcare',
                'keywords' => ['regulatory compliance', 'security protocols', 'auditing']
            ]
        ];

        foreach ($healthcareTopics as $topic) {
            Topic::create([
                'name' => $topic['name'],
                'description' => $topic['description'],
                'keywords' => json_encode($topic['keywords']),
                'sector_id' => $healthcareSector->id
            ]);
        }

        // Travel sector topics
        $travelSector = Sector::where('name', 'Travel')->first();
        $travelTopics = [
            [
                'name' => 'Booking System Security',
                'description' => 'Protecting travel booking platforms and customer data',
                'keywords' => ['payment security', 'booking fraud', 'customer data']
            ],
            [
                'name' => 'Travel Document Security',
                'description' => 'Safeguarding passports, visas, and other travel documents',
                'keywords' => ['identity theft', 'document protection', 'travel papers']
            ],
            [
                'name' => 'Hotel Wi-Fi Safety',
                'description' => 'Staying secure when using hotel and public Wi-Fi',
                'keywords' => ['public networks', 'VPN', 'secure connections']
            ]
        ];

        foreach ($travelTopics as $topic) {
            Topic::create([
                'name' => $topic['name'],
                'description' => $topic['description'],
                'keywords' => json_encode($topic['keywords']),
                'sector_id' => $travelSector->id
            ]);
        }

        // Finance sector topics
        $financeSector = Sector::where('name', 'Finance')->first();
        $financeTopics = [
            [
                'name' => 'Investment Fraud Prevention',
                'description' => 'Recognizing and avoiding fraudulent investment schemes',
                'keywords' => ['ponzi schemes', 'investment scams', 'due diligence']
            ],
            [
                'name' => 'Insider Trading Prevention',
                'description' => 'Understanding and preventing illegal insider trading',
                'keywords' => ['material information', 'trading regulations', 'legal compliance']
            ],
            [
                'name' => 'Client Data Security',
                'description' => 'Protecting sensitive client financial information',
                'keywords' => ['financial data', 'client confidentiality', 'data access controls']
            ]
        ];

        foreach ($financeTopics as $topic) {
            Topic::create([
                'name' => $topic['name'],
                'description' => $topic['description'],
                'keywords' => json_encode($topic['keywords']),
                'sector_id' => $financeSector->id
            ]);
        }
    }
}
