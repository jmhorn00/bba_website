from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from .forms import ContactForm


def submit_contact(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    form = ContactForm(request.POST)
    if not form.is_valid():
        return render(request, 'contact/partials/_form.html', {'form': form})

    data = form.cleaned_data
    _send_contact_emails(data)

    return render(request, 'contact/partials/_success.html', {'name': data['name']})


def _send_contact_emails(data):
    if not settings.RESEND_API_KEY:
        return

    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY

        service_label = dict([
            ('tax', 'Tax Services'), ('audit', 'Audit & Assurance'),
            ('advisory', 'Business Advisory'), ('estate', 'Estate & Trust'),
            ('corporate', 'Corporate Tax'), ('reporting', 'Financial Reporting'),
            ('payroll', 'Payroll Services'), ('other', 'Other'),
        ]).get(data.get('service', ''), data.get('service', ''))

        # Firm notification
        resend.Emails.send({
            'from': 'noreply@bbacpas.com',
            'to': [settings.CONTACT_EMAIL],
            'subject': f'New Contact Form Submission — {data["name"]}',
            'html': f"""
                <h2>New Contact Form Submission</h2>
                <p><strong>Name:</strong> {data["name"]}</p>
                <p><strong>Email:</strong> {data["email"]}</p>
                <p><strong>Phone:</strong> {data.get("phone") or "Not provided"}</p>
                <p><strong>Service of Interest:</strong> {service_label}</p>
                <hr>
                <p><strong>Message:</strong></p>
                <p>{data["message"]}</p>
            """,
        })

        # Auto-reply to submitter
        resend.Emails.send({
            'from': 'noreply@bbacpas.com',
            'to': [data['email']],
            'subject': 'We received your message — BBA CPAs',
            'html': f"""
                <h2>Thank you, {data["name"]}!</h2>
                <p>We have received your message and will be in touch shortly.</p>
                <p>If your matter is urgent, please call us directly at (724) 555-0100.</p>
                <br>
                <p>— Brunner, Blackstone &amp; Associates, PC</p>
                <p style="color:#888; font-size:12px;">{settings.CONTACT_EMAIL}</p>
            """,
        })
    except Exception:
        pass  # Don't let email failure break the form submission
