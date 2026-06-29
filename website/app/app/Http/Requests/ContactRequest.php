<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class ContactRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'name' => ['required', 'string', 'max:100'],
            'phone' => ['required', 'string', 'max:30'],
            'business_name' => ['required', 'string', 'max:150'],
            'location' => ['required', 'string', 'max:150'],
            'industry' => ['required', 'string', 'max:50'],
            'message' => ['nullable', 'string', 'max:2000'],
        ];
    }

    public function messages(): array
    {
        return [
            'name.required' => 'Please enter your name.',
            'phone.required' => 'Please enter a phone number so we can reach you.',
            'business_name.required' => 'Please enter your business name.',
            'location.required' => 'Please enter your city and state.',
            'industry.required' => 'Please select your industry.',
        ];
    }
}
