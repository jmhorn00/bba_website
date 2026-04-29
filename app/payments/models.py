from django.db import models


class PaymentRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    stripe_session_id = models.CharField(max_length=200, unique=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='Invoice # provided by client',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client_name} — ${self.amount} — {self.invoice_number} ({self.status})'
