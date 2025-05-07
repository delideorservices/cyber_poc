<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Certification;

class CertificationSeeder extends Seeder
{
    public function run()
    {
        $certifications = [
            [
                'name' => 'CompTIA Security+',
                'provider' => 'CompTIA',
                'description' => 'Foundational IT security certification'
            ],
            [
                'name' => 'Certified Information Systems Security Professional (CISSP)',
                'provider' => 'ISC2',
                'description' => 'Advanced security certification'
            ],
            [
                'name' => 'Certified Ethical Hacker (CEH)',
                'provider' => 'EC-Council',
                'description' => 'Ethical hacking and penetration testing certification'
            ],
            [
                'name' => 'Certified Information Security Manager (CISM)',
                'provider' => 'ISACA',
                'description' => 'Security management certification'
            ],
            [
                'name' => 'Certified Cloud Security Professional (CCSP)',
                'provider' => 'ISC2',
                'description' => 'Cloud security certification'
            ],
            [
                'name' => 'GIAC Security Essentials (GSEC)',
                'provider' => 'SANS Institute',
                'description' => 'Fundamental security skills certification'
            ],
            [
                'name' => 'Certified Information Privacy Professional (CIPP)',
                'provider' => 'IAPP',
                'description' => 'Privacy law and practice certification'
            ]
        ];

        foreach ($certifications as $certification) {
            Certification::create($certification);
        }
    }
}
