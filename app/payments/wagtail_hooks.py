from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import PaymentRecord


class PaymentRecordViewSet(SnippetViewSet):
    model = PaymentRecord
    icon = 'form'
    menu_label = 'Payment History'
    add_to_admin_menu = True
    list_display = ['client_name', 'client_email', 'invoice_number', 'amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['client_name', 'client_email', 'invoice_number']
    ordering = ['-created_at']


register_snippet(PaymentRecordViewSet)
