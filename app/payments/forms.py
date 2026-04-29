from decimal import Decimal

from django import forms


class PaymentForm(forms.Form):
    client_name = forms.CharField(
        max_length=100,
        label='Your Full Name',
        widget=forms.TextInput(attrs={'placeholder': 'Jane Smith'}),
    )
    client_email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'placeholder': 'jane@example.com'}),
    )
    invoice_number = forms.CharField(
        max_length=100,
        required=False,
        label='Invoice Number',
        help_text='Found on your invoice from BBA CPAs (optional but recommended)',
        widget=forms.TextInput(attrs={'placeholder': 'INV-2024-001'}),
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('1.00'),
        label='Payment Amount',
        widget=forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional details about this payment (optional)'}),
        label='Note (optional)',
        help_text='Any additional details about this payment',
    )
