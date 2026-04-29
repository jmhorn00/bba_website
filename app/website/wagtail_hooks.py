from django.utils.safestring import mark_safe

from wagtail import hooks
from wagtail.admin.ui.components import Component


class WelcomePanel(Component):
    order = 50

    def render_html(self, parent_context=None):
        return mark_safe("""
        <div style="padding:16px 20px; background:#f7f5f0; border-left:4px solid #c9a84c;
                    border-radius:4px; margin-bottom:16px; font-family: sans-serif;">
          <strong style="color:#1c3a5e;">Welcome to the BBA CPAs website editor.</strong><br><br>
          Use the <strong>Pages</strong> menu on the left to edit content on any page of the site.<br><br>
          <strong>Common tasks:</strong>
          <ul style="margin: 8px 0 0 20px; color: #333;">
            <li>Update homepage content: Pages &rarr; Home</li>
            <li>Add team members: Pages &rarr; Home &rarr; About</li>
            <li>Add newsletter articles: Pages &rarr; Home &rarr; Newsletters</li>
            <li>Update job postings: Pages &rarr; Home &rarr; Careers</li>
            <li>View payment history: Snippets &rarr; Payment History</li>
          </ul>
          <br>
          <span style="color:#888; font-size: 13px;">
            Contact your developer for layout or structural changes.
          </span>
        </div>
        """)


@hooks.register('construct_homepage_panels')
def add_welcome_panel(request, panels):
    panels.insert(0, WelcomePanel())
