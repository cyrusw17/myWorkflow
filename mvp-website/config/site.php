<?php

return [
    'name' => 'Groundwork Web',
    'founder' => 'Cyrus',
    'tagline' => 'Custom websites for local service businesses — built, hosted, and maintained for you.',
    'email' => getenv('SITE_EMAIL') ?: 'hello@groundwork-web.com',
    'url' => getenv('SITE_URL') ?: 'https://groundwork-web.com',
    'calendly_url' => getenv('CALENDLY_URL') ?: '',

    'offer' => [
        'name' => 'Founding Client Program',
        'spots_total' => 3,
        'spots_remaining' => 2,
        'setup_normal' => 2500,
        'monthly' => 199,
        'term_months' => 12,
        'build_weeks' => '2–4',
    ],

    'industries' => [
        'Automotive shops', 'Detailers', 'HVAC', 'Electricians',
        'Contractors', 'Roofers', 'Plumbing', 'Local trades',
    ],

    'included' => [
        'featured' => [
            ['title' => 'Custom 5-page website', 'body' => 'Designed and coded for your business — not a drag-and-drop template.', 'icon' => 'layout'],
            ['title' => 'Built for phone calls', 'body' => 'Clear CTAs, click-to-call, and mobile-first layout so customers reach you fast.', 'icon' => 'phone'],
            ['title' => 'We run it monthly', 'body' => 'Hosting, SSL, security, updates, and support — one bill, zero headaches.', 'icon' => 'shield'],
        ],
        'also' => [
            'SEO-ready structure', 'Contact & lead forms', 'Fast loading performance',
            'Security monitoring', 'Ongoing updates', 'Performance optimization',
            'Dedicated technical support', 'Minor content changes',
        ],
    ],

    'how_it_works' => [
        ['step' => '01', 'title' => 'Apply', 'body' => 'Fill out a short form. Tell us how and when to reach you — no pressure.'],
        ['step' => '02', 'title' => 'Plan & design', 'body' => 'We map your pages, messaging, and design before a single line of code.'],
        ['step' => '03', 'title' => 'Build & launch', 'body' => 'Custom site goes live on your domain in 2–4 weeks.'],
        ['step' => '04', 'title' => 'We run it', 'body' => 'Hosting, updates, and maintenance every month — you stay focused on the shop.'],
    ],

    'custom_benefits' => [
        ['title' => 'Performance', 'body' => 'Clean code loads fast. Speed affects Google rankings and whether customers stay.'],
        ['title' => 'SEO foundation', 'body' => 'Built with structure search engines understand — not an afterthought.'],
        ['title' => 'Unique branding', 'body' => 'Your business looks like your business — not a template with your logo pasted on.'],
        ['title' => 'Full control', 'body' => 'No platform lock-in. Your site is yours, built to scale as you grow.'],
    ],

    'faqs' => [
        [
            'q' => 'Why is there no setup fee?',
            'a' => 'We\'re accepting three founding clients to build our portfolio with real local businesses. In exchange for waiving the setup fee, we ask for a testimonial, permission to feature your business as a case study, and a 12-month partnership.',
        ],
        [
            'q' => 'Why only three spots?',
            'a' => 'Founding clients get white-glove attention. We can only deliver that level of service to three businesses at launch while maintaining quality standards.',
        ],
        [
            'q' => 'Can I cancel anytime?',
            'a' => 'The founding program requires a 12-month commitment at $199/month. After that, it continues month-to-month. We\'re looking for long-term partners, not one-off projects.',
        ],
        [
            'q' => 'How long does the build take?',
            'a' => 'Typically 2–4 weeks from kickoff, depending on how quickly you provide photos, content, and feedback.',
        ],
        [
            'q' => 'What\'s included in $199/month?',
            'a' => 'Hosting, SSL, security updates, uptime monitoring, maintenance, minor content changes, and technical support. We keep your site running so you don\'t have to think about it.',
        ],
        [
            'q' => 'What isn\'t included?',
            'a' => 'Major redesigns, unlimited revision rounds, e-commerce, custom apps, and paid ad management are outside the founding scope. We\'ll be upfront about anything extra when we talk.',
        ],
        [
            'q' => 'Who owns the website?',
            'a' => 'You do. Your domain, your content, your business. We build and manage it as your partner.',
        ],
        [
            'q' => 'Can I upgrade later?',
            'a' => 'Yes. After launch we can add pages, SEO campaigns, automation, and other growth services as your business scales.',
        ],
    ],

    'form_industries' => [
        'Automotive / mechanic',
        'Detailing',
        'HVAC',
        'Electrical',
        'Plumbing',
        'Roofing',
        'General contractor',
        'Landscaping',
        'Other local service',
    ],

    'form_contact_methods' => [
        'phone' => 'Phone call',
        'text' => 'Text message',
        'email' => 'Email',
    ],

    'form_contact_times' => [
        'morning' => 'Morning (8am–12pm)',
        'afternoon' => 'Afternoon (12pm–5pm)',
        'evening' => 'Evening (5pm–8pm)',
        'anytime' => 'Anytime works',
    ],
];
