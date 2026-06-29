New contact form submission — Groundwork Web

Name: {{ $lead->name }}
Phone: {{ $lead->phone }}
Business: {{ $lead->business_name }}
Location: {{ $lead->location }}
Industry: {{ $lead->industry }}

Message:
{{ $lead->message ?: '(none)' }}

Submitted: {{ $lead->created_at }}
