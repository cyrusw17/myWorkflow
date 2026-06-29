<?php

return [
    'name' => env('APP_NAME', 'Groundwork Web'),
    'tagline' => 'Builds and runs websites for local service businesses — more leads, zero tech hassle.',
    'email' => 'hello@groundwork-web.com',
    'service_area' => 'Serving businesses across the United States',
    'calendly_url' => env('CALENDLY_URL', ''),
    'lead_to' => env('MAIL_LEAD_TO', 'hello@groundwork-web.com'),

    'pricing' => [
        'build' => 2500,
        'growth_monthly' => 199,
    ],

    'industries' => [
        ['title' => 'Auto shops & mechanics', 'icon' => 'wrench'],
        ['title' => 'Contractors & roofers', 'icon' => 'hammer'],
        ['title' => 'HVAC & trades', 'icon' => 'thermometer'],
        ['title' => 'Local pros & services', 'icon' => 'building'],
    ],

    'pain_points' => [
        ['title' => "Customers can't find you online", 'body' => 'Competitors show up on Google and maps — you miss the calls.'],
        ['title' => 'Your site looks outdated on mobile', 'body' => 'A broken first impression costs trust before they ever walk in.'],
        ['title' => "You don't have time for website stuff", 'body' => "You're running the business — not learning plugins and hosting."],
    ],

    'system_layers' => [
        ['key' => 'build', 'title' => 'Build', 'body' => 'Custom-coded website built for calls — mobile, fast, clear CTAs.'],
        ['key' => 'run', 'title' => 'Run', 'body' => 'Hosting, SSL, backups, and uptime monitoring.'],
        ['key' => 'maintain', 'title' => 'Maintain', 'body' => 'Updates, fixes, and security — you never touch it.'],
        ['key' => 'grow', 'title' => 'Grow', 'body' => 'SEO foundations and Google Business Profile guidance.'],
    ],

    'process_steps' => [
        ['step' => '01', 'title' => 'Discovery', 'body' => '30-minute call. We learn your business and goals.'],
        ['step' => '02', 'title' => 'Build', 'body' => 'Custom site designed to bring in calls.'],
        ['step' => '03', 'title' => 'Launch', 'body' => 'Go live on your domain — ready for customers.'],
        ['step' => '04', 'title' => 'We run it', 'body' => 'Hosting, updates, and maintenance every month.'],
    ],

    'comparison' => [
        'diy' => [
            'You maintain it',
            'Looks like everyone else',
            'Plugin and downtime problems',
            'Your time is not saved',
        ],
        'us' => [
            'We build AND run it',
            'Custom-coded for speed',
            'Built for phone calls',
            'Your time stays on the business',
        ],
    ],

    'faqs' => [
        [
            'q' => 'How much does a website cost?',
            'a' => 'Most projects start at $2,500 for the build plus $199/month for hosting and maintenance. Final pricing depends on scope — pages, integrations, and content. We quote on your discovery call.',
        ],
        [
            'q' => 'How long does it take to build?',
            'a' => 'Typical builds take 2–4 weeks depending on scope and how quickly you can provide photos and content.',
        ],
        [
            'q' => "What's included in the monthly plan?",
            'a' => 'Hosting, SSL, backups, uptime monitoring, security updates, and minor content changes. We keep your site running so you do not have to think about it.',
        ],
        [
            'q' => 'I already have a website — can you help?',
            'a' => 'Yes. We can rebuild, redesign, or take over hosting and maintenance. We will audit what you have on the discovery call.',
        ],
        [
            'q' => 'Why not just use Wix or Squarespace?',
            'a' => 'Templates still require your time, often load slower, and look generic. We build custom sites optimized for calls — and we run everything for you monthly.',
        ],
        [
            'q' => 'What happens on the discovery call?',
            'a' => 'We learn about your business, look at your current online presence, and tell you honestly what we recommend — including if we are not the right fit. No pressure.',
        ],
    ],

    'form_industries' => [
        'Auto repair / mechanic',
        'Detailing / performance',
        'HVAC',
        'Roofing / contractor',
        'Electrical',
        'Landscaping',
        'Other local service',
    ],
];
