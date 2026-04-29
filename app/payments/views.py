import stripe
from django.conf import settings
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .forms import PaymentForm
from .models import PaymentRecord


def pay(request):
    form = PaymentForm()
    return render(request, 'payments/pay.html', {'form': form})


def create_checkout_session(request):
    if request.method != 'POST':
        return redirect('payments:pay')

    form = PaymentForm(request.POST)
    if not form.is_valid():
        return render(request, 'payments/pay.html', {'form': form})

    data = form.cleaned_data
    stripe.api_key = settings.STRIPE_SECRET_KEY

    amount_cents = int(data['amount'] * 100)

    invoice_desc = (
        f"Invoice #{data['invoice_number']}"
        if data.get('invoice_number')
        else 'Professional Services Payment'
    )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': amount_cents,
                    'product_data': {
                        'name': 'BBA CPAs — Invoice Payment',
                        'description': invoice_desc,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_email=data['client_email'],
            metadata={
                'client_name': data['client_name'],
                'client_email': data['client_email'],
                'invoice_number': data.get('invoice_number', ''),
                'note': data.get('note', ''),
            },
            success_url=request.build_absolute_uri('/pay/success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/pay/cancel/'),
        )
    except stripe.error.StripeError as e:
        form.add_error(None, f'Payment error: {e.user_message}')
        return render(request, 'payments/pay.html', {'form': form})

    PaymentRecord.objects.create(
        stripe_session_id=session.id,
        client_name=data['client_name'],
        client_email=data['client_email'],
        invoice_number=data.get('invoice_number', ''),
        amount=data['amount'],
        note=data.get('note', ''),
        status='pending',
    )

    return redirect(session.url, permanent=False)


def payment_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('payments:pay')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        return redirect('payments:pay')

    record = PaymentRecord.objects.filter(stripe_session_id=session_id).first()
    if record and record.status == 'pending':
        record.status = 'complete'
        record.stripe_payment_intent = session.payment_intent or ''
        record.completed_at = timezone.now()
        record.save()
        _send_payment_emails(record)

    return render(request, 'payments/success.html', {'record': record, 'session': session})


def payment_cancel(request):
    return render(request, 'payments/cancel.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        record = PaymentRecord.objects.filter(
            stripe_session_id=session['id'],
            status='pending',
        ).first()
        if record:
            record.status = 'complete'
            record.stripe_payment_intent = session.get('payment_intent', '')
            record.completed_at = timezone.now()
            record.save()
            _send_payment_emails(record)

    return HttpResponse(status=200)


def _send_payment_emails(record):
    if not settings.RESEND_API_KEY:
        return

    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY

        # Firm notification
        resend.Emails.send({
            'from': 'noreply@bbacpas.com',
            'to': [settings.CONTACT_EMAIL],
            'subject': f'Payment Received — {record.client_name} — ${record.amount}',
            'html': f"""
                <h2>Payment Received</h2>
                <table cellpadding="6" style="border-collapse:collapse;">
                    <tr><td><strong>Client:</strong></td><td>{record.client_name} ({record.client_email})</td></tr>
                    <tr><td><strong>Invoice #:</strong></td><td>{record.invoice_number or 'Not provided'}</td></tr>
                    <tr><td><strong>Amount:</strong></td><td>${record.amount}</td></tr>
                    <tr><td><strong>Note:</strong></td><td>{record.note or '—'}</td></tr>
                    <tr><td><strong>Stripe Session:</strong></td><td>{record.stripe_session_id}</td></tr>
                </table>
            """,
        })

        # Client confirmation
        invoice_line = f'<p><strong>Invoice #:</strong> {record.invoice_number}</p>' if record.invoice_number else ''
        resend.Emails.send({
            'from': 'noreply@bbacpas.com',
            'to': [record.client_email],
            'subject': 'Payment Confirmation — BBA CPAs',
            'html': f"""
                <h2>Thank you, {record.client_name}!</h2>
                <p>We have received your payment of <strong>${record.amount}</strong>.</p>
                {invoice_line}
                <p>Please retain this email for your records.</p>
                <p>If you have any questions, contact us at {settings.CONTACT_EMAIL} or call (724) 555-0100.</p>
                <br>
                <p>— Brunner, Blackstone &amp; Associates, PC</p>
            """,
        })
    except Exception:
        pass
