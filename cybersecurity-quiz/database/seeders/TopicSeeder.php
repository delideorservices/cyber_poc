<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Topic;
use App\Models\Sector;

class TopicSeeder extends Seeder
{
    public function run()
    {
        // Cybersecurity topics from the interface
        $cyberTopics = [
            [
                'name' => 'Email Fraud',
                'description' => 'Detecting and preventing fraudulent email schemes and attacks',
                'keywords' => ['phishing', 'spoofing', 'spam', 'malicious attachments', 'email security']
            ],
            [
                'name' => 'Identity Fraud',
                'description' => 'Protecting personal identities from theft and fraudulent use',
                'keywords' => ['identity theft', 'impersonation', 'personal data', 'document theft', 'verification']
            ],
            [
                'name' => 'Corporate Data',
                'description' => 'Securing sensitive corporate information and preventing data breaches',
                'keywords' => ['data breach', 'corporate espionage', 'intellectual property', 'trade secrets', 'data security']
            ],
            [
                'name' => 'Personal Information Hacking',
                'description' => 'Safeguarding personal information from unauthorized access and theft',
                'keywords' => ['personal data', 'privacy', 'data protection', 'information security', 'hacking']
            ],
            [
                'name' => 'Crypto Jacking',
                'description' => 'Preventing unauthorized use of computing resources to mine cryptocurrency',
                'keywords' => ['cryptocurrency', 'mining', 'malware', 'resource hijacking', 'performance issues']
            ],
            [
                'name' => 'Business Email Compromise',
                'description' => 'Preventing targeted email attacks against businesses to conduct fraud',
                'keywords' => ['CEO fraud', 'email security', 'wire fraud', 'financial scams', 'impersonation']
            ],
            [
                'name' => 'Card Payment Theft',
                'description' => 'Protecting against credit card fraud and payment information theft',
                'keywords' => ['credit card fraud', 'skimming', 'payment security', 'card verification', 'PCI compliance']
            ],
            [
                'name' => 'Cyber Extortion',
                'description' => 'Dealing with threats involving ransomware and digital blackmail',
                'keywords' => ['ransomware', 'blackmail', 'data encryption', 'payment demands', 'threat response']
            ],
            [
                'name' => 'Cyber Espionage',
                'description' => 'Countering state-sponsored and corporate spying in digital environments',
                'keywords' => ['state actors', 'APTs', 'sensitive information', 'industrial espionage', 'national security']
            ],
            [
                'name' => 'Crypto Red Flags And AML',
                'description' => 'Identifying suspicious cryptocurrency activities and preventing money laundering',
                'keywords' => ['anti-money laundering', 'cryptocurrency', 'suspicious transactions', 'compliance', 'regulation']
            ]
        ];

        // Create all topics
        foreach ($cyberTopics as $topic) {
            Topic::create([
                'name' => $topic['name'],
                'description' => $topic['description'],
                'keywords' => json_encode($topic['keywords'])
            ]);
        }

        // If you want to associate some topics with specific sectors (optional)
        // For example:
        
        $financeSector = Sector::where('name', 'Finance')->first();
        if ($financeSector) {
            // Find the topics related to finance and associate them
            $financeTopics = ['Card Payment Theft', 'Crypto Red Flags And AML'];
            
            foreach ($financeTopics as $topicName) {
                $topic = Topic::where('name', $topicName)->first();
                if ($topic) {
                    $topic->sector_id = $financeSector->id;
                    $topic->save();
                }
            }
        }
        
        $corporateSector = Sector::where('name', 'Corporate')->first();
        if ($corporateSector) {
            // Find topics related to corporate security
            $corporateTopics = ['Business Email Compromise', 'Corporate Data', 'Cyber Espionage'];
            
            foreach ($corporateTopics as $topicName) {
                $topic = Topic::where('name', $topicName)->first();
                if ($topic) {
                    $topic->sector_id = $corporateSector->id;
                    $topic->save();
                }
            }
        }
    }
}