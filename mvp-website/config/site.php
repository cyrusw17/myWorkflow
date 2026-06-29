<?php

return [
    'name' => 'Groundwork Web',
    'founder' => 'Cyrus',
    'tagline' => 'We build and run websites for local service businesses — so you get more customers without touching the tech.',
    'email' => getenv('SITE_EMAIL') ?: 'hello@groundwork-web.com',
    'url' => getenv('SITE_URL') ?: 'https://groundwork-web.com',
    // Live business number. Env vars can override per-environment if ever needed.
    'phone_display' => getenv('SITE_PHONE_DISPLAY') ?: '(270) 801-9780',
    'phone_sms' => getenv('SITE_PHONE_SMS') ?: '12708019780',
    'sms_keyword' => 'LAUNCH',

    'offer' => [
        'name' => 'Launch Partner Program',
        'spots_total' => 3,
        'spots_remaining' => 2,
        'setup_normal' => 2500,
        'monthly' => 199,
        'term_months' => 12,
        'build_weeks' => '2–4',
    ],

    'hero' => [
        'headline' => 'Get More Calls. Look More Professional. Grow Your Business.',
        'subhead' => 'We partner with three local service businesses to build a custom lead-generating website — with no setup fee in exchange for a testimonial and case study.',
    ],

    'why_exists' => [
        'lead' => 'Instead of spending thousands on ads trying to convince strangers to trust us, we\'re investing that value into three local businesses we can do our best work for.',
        'exchange' => [
            'A written testimonial when your site launches',
            'Permission to showcase your business as a case study',
            'A 12-month partnership so we can prove long-term results',
        ],
    ],

    'included' => [
        'Custom 5-page website',
        'Mobile-first design',
        'Built to generate leads',
        'Hosting & SSL',
        'Maintenance & updates',
        'Unlimited technical support',
        'Fast performance',
        'SEO foundation',
        'Security monitoring',
    ],

    'how_it_works' => [
        ['step' => '01', 'title' => 'Text us', 'body' => 'Send "LAUNCH" to start a conversation on your schedule — no phone tag, no meetings required upfront.'],
        ['step' => '02', 'title' => 'Quick qualification', 'body' => 'We ask a few questions to make sure we\'re the right fit for your business and timeline.'],
        ['step' => '03', 'title' => 'Strategy', 'body' => 'We map your pages, messaging, and design around what actually brings you customers.'],
        ['step' => '04', 'title' => 'Build', 'body' => 'Your custom site comes together in about 2–4 weeks with clear checkpoints along the way.'],
        ['step' => '05', 'title' => 'Launch', 'body' => 'We go live on your domain and handle hosting, maintenance, and support every month after.'],
    ],

    'trust' => [
        ['title' => 'Transparent pricing', 'body' => 'You see the full price upfront. $0 setup, $199/month. Nothing hidden.'],
        ['title' => 'No hidden fees', 'body' => 'One flat monthly plan covers hosting, maintenance, and support.'],
        ['title' => 'Custom built — not templates', 'body' => 'Your site is designed and built for your business, not dragged from a template.'],
        ['title' => 'Long-term support', 'body' => 'We maintain, update, and support your site every month after launch.'],
        ['title' => 'Direct communication', 'body' => 'You talk to the person building your site — no call centers, no runaround.'],
        ['title' => 'Secure hosting', 'body' => 'SSL, security monitoring, and reliable hosting handled for you.'],
        ['title' => 'Mobile optimized', 'body' => 'Most of your customers are on a phone. Your site is built for them first.'],
        ['title' => 'Honest qualification', 'body' => 'If we\'re not the right fit, we\'ll tell you. No pressure, no hard sell.'],
    ],

    'custom_benefits' => [
        ['title' => 'Room to grow', 'body' => 'A custom site grows with your business — new services, new locations, new offers — without fighting a template\'s limits.'],
        ['title' => 'Built for trust', 'body' => 'Customers judge your business in seconds. A professional site makes you look established before they ever pick up the phone.'],
        ['title' => 'More leads, less hassle', 'body' => 'Clear calls-to-action, fast mobile experience, and a layout designed to turn visitors into customers — not just look pretty.'],
        ['title' => 'You own it', 'body' => 'Your domain, your content, your business. We build and manage it as your partner — you\'re never locked into a DIY builder.'],
    ],

    'faqs' => [
        [
            'q' => 'Why is there no setup fee?',
            'a' => 'We\'re partnering with three local businesses to build real case studies. In exchange for waiving the $2,500+ setup fee, we ask for a testimonial, permission to feature your project, and a 12-month partnership.',
        ],
        [
            'q' => 'Why only three businesses?',
            'a' => 'Launch Partners get focused attention. We can only deliver white-glove service to three businesses at once while maintaining the quality we\'d want on our own site.',
        ],
        [
            'q' => 'Who owns the website?',
            'a' => 'You do. Your domain, your content, your business. We build and manage it as your partner.',
        ],
        [
            'q' => 'How long does it take?',
            'a' => 'Typically 2–4 weeks from kickoff, depending on how quickly you provide photos, content, and feedback.',
        ],
        [
            'q' => 'Can I request changes?',
            'a' => 'Yes. The Launch Partner scope includes one design round and two revision rounds. Minor content updates are included in your monthly plan after launch.',
        ],
        [
            'q' => 'What happens after twelve months?',
            'a' => 'Your plan continues month-to-month at $199/mo. We keep hosting, maintaining, and supporting your site — you\'re never forced into a rebuild.',
        ],
        [
            'q' => 'What\'s included in $199/month?',
            'a' => 'Hosting, SSL, security updates, maintenance, minor content changes, and unlimited technical support. We keep your site running so you can focus on the business.',
        ],
        [
            'q' => 'What isn\'t included?',
            'a' => 'Major redesigns, unlimited revision rounds, e-commerce, custom apps, and paid ad management are outside the Launch Partner scope. We\'ll be upfront about anything extra.',
        ],
    ],

    'qualify_industries' => [
        'Auto repair / mechanic',
        'Detailing',
        'HVAC',
        'Electrical',
        'Plumbing',
        'Roofing',
        'General contractor',
        'Landscaping',
        'Pressure washing',
        'Other local service',
    ],
];
