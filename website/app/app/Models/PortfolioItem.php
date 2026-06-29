<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class PortfolioItem extends Model
{
    protected $fillable = [
        'slug',
        'title',
        'industry',
        'tagline',
        'challenge',
        'approach',
        'goals',
        'is_concept',
        'published',
        'gallery',
        'sort_order',
    ];

    protected function casts(): array
    {
        return [
            'is_concept' => 'boolean',
            'published' => 'boolean',
            'gallery' => 'array',
        ];
    }

    public function scopePublished(Builder $query): Builder
    {
        return $query->where('published', true);
    }

    public function scopeOrdered(Builder $query): Builder
    {
        return $query->orderBy('sort_order')->orderBy('title');
    }
}
