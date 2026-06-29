<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Lead extends Model
{
    protected $fillable = [
        'name',
        'phone',
        'business_name',
        'location',
        'industry',
        'message',
        'source',
        'status',
        'ip_address',
    ];
}
