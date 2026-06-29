<?php

namespace App\Http\Controllers;

use App\Http\Requests\ContactRequest;
use App\Mail\LeadReceived;
use App\Models\Lead;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Mail;

class ContactController extends Controller
{
    public function store(ContactRequest $request): RedirectResponse
    {
        $lead = Lead::create([
            ...$request->validated(),
            'source' => 'contact_form',
            'status' => 'new',
            'ip_address' => $request->ip(),
        ]);

        $to = config('site.lead_to');
        if ($to) {
            Mail::to($to)->send(new LeadReceived($lead));
        }

        return redirect()
            ->route('contact')
            ->withFragment('form')
            ->with('success', "Thanks, {$lead->name} — we'll be in touch within 24 hours to schedule your call.");
    }
}
