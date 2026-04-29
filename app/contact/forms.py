from django import forms


SERVICE_CHOICES = [
    ('', 'Select a service...'),
    ('tax', 'Tax Services'),
    ('audit', 'Audit & Assurance'),
    ('advisory', 'Business Advisory'),
    ('estate', 'Estate & Trust'),
    ('corporate', 'Corporate Tax'),
    ('reporting', 'Financial Reporting'),
    ('payroll', 'Payroll Services'),
    ('other', 'Other'),
]


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Full Name',
        widget=forms.TextInput(attrs={'placeholder': 'Jane Smith'}),
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'placeholder': 'jane@example.com'}),
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        label='Phone (optional)',
        widget=forms.TextInput(attrs={'placeholder': '(724) 555-0100'}),
    )
    service = forms.ChoiceField(choices=SERVICE_CHOICES)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'How can we help you?'}),
        label='Message',
    )
