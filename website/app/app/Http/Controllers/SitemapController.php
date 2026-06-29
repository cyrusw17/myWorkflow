<?php

namespace App\Http\Controllers;

use App\Models\PortfolioItem;
use Illuminate\Http\Response;

class SitemapController extends Controller
{
    public function index(): Response
    {
        $urls = [
            ['loc' => url('/'), 'priority' => '1.0'],
            ['loc' => route('services'), 'priority' => '0.9'],
            ['loc' => route('work'), 'priority' => '0.9'],
            ['loc' => route('about'), 'priority' => '0.7'],
            ['loc' => route('contact'), 'priority' => '0.8'],
        ];

        foreach (PortfolioItem::published()->get() as $item) {
            $urls[] = [
                'loc' => route('work.show', $item->slug),
                'priority' => '0.8',
            ];
        }

        return response()
            ->view('sitemap', ['urls' => $urls])
            ->header('Content-Type', 'application/xml');
    }

    public function robots(): Response
    {
        $content = "User-agent: *\nAllow: /\n\nSitemap: ".url('/sitemap.xml')."\n";

        return response($content, 200, ['Content-Type' => 'text/plain']);
    }
}
