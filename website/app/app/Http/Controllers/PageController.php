<?php

namespace App\Http\Controllers;

use App\Models\PortfolioItem;
use Illuminate\View\View;

class PageController extends Controller
{
    public function home(): View
    {
        $featured = PortfolioItem::published()->ordered()->first();

        return view('pages.home', [
            'featured' => $featured,
            'meta' => [
                'title' => 'Groundwork Web | Websites for Local Service Businesses',
                'description' => 'Custom websites for shops and trades — built for more calls, hosted and maintained for you. Book a free discovery call.',
            ],
        ]);
    }

    public function services(): View
    {
        return view('pages.services', [
            'meta' => [
                'title' => 'Services & Pricing | Groundwork Web',
                'description' => 'Website build, hosting, and maintenance for local businesses. Starting at $2,500 + $199/mo.',
            ],
        ]);
    }

    public function work(): View
    {
        $projects = PortfolioItem::published()->ordered()->get();

        return view('pages.work.index', [
            'projects' => $projects,
            'meta' => [
                'title' => 'Our Work | Groundwork Web',
                'description' => 'Websites built for local service businesses — designed to drive phone calls and trust.',
            ],
        ]);
    }

    public function workShow(string $slug): View
    {
        $project = PortfolioItem::published()->where('slug', $slug)->firstOrFail();

        return view('pages.work.show', [
            'project' => $project,
            'meta' => [
                'title' => $project->title.' | Groundwork Web',
                'description' => $project->tagline,
            ],
        ]);
    }

    public function about(): View
    {
        return view('pages.about', [
            'meta' => [
                'title' => 'About | Groundwork Web',
                'description' => 'Groundwork Web helps local shop and trade owners get more leads without website headaches.',
            ],
        ]);
    }

    public function contact(): View
    {
        return view('pages.contact', [
            'meta' => [
                'title' => 'Contact | Groundwork Web',
                'description' => 'Get in touch or request a free discovery call. We serve local businesses across the United States.',
            ],
        ]);
    }
}
