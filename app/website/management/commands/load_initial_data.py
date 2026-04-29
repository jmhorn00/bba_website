"""
Management command: python manage.py load_initial_data

Creates the full Wagtail page tree with seed content for the BBA CPAs website.
Safe to re-run — existing pages are detected and skipped.
"""

import json

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from wagtail.models import Page, Site


def _stream_json(*blocks):
    return json.dumps(list(blocks))


def _block(block_type, **value):
    return {'type': block_type, 'value': value}


class Command(BaseCommand):
    help = 'Load initial BBA CPAs site content into Wagtail'

    def handle(self, *args, **options):
        self.stdout.write('Loading initial data for BBA CPAs...')

        # ── Imports after Django is ready ────────────────────────────────────
        from website.models import (
            AboutPage, CareersPage, ContactPage, FinancialToolsPage,
            HomePage, LinksPage, NewslettersPage, ResourceCenterPage,
            ServicesPage,
        )

        # ── Get or set up Wagtail root ────────────────────────────────────────
        try:
            root = Page.objects.get(depth=1)
        except Page.DoesNotExist:
            self.stderr.write('Wagtail root page not found. Run migrations first.')
            return

        # ── Create HomePage ───────────────────────────────────────────────────
        if HomePage.objects.exists():
            home = HomePage.objects.first()
            self.stdout.write(f'  HomePage already exists (id={home.pk})')
        else:
            home = HomePage(
                title='Home',
                slug='home',
                hero_headline='Precision. Integrity. Results.',
                hero_subheadline='<p>Expert tax, audit, and advisory services from CPAs who put your success first. '
                                 'Partners personally involved in every engagement.</p>',
                hero_cta_text='Schedule a Consultation',
                hero_stat_1_number='30+',
                hero_stat_1_label='Years of Experience',
                hero_stat_2_number='500+',
                hero_stat_2_label='Clients Served',
                hero_stat_3_number='50',
                hero_stat_3_label='States Served',
                why_headline='Why Choose BB&A?',
                why_body='<p>We combine the depth of a large firm with the personal attention '
                         'of a boutique practice. Partners are involved in every engagement, '
                         'and we stay current on all regulatory changes so you can focus on '
                         'what matters most.</p>',
                why_items=json.dumps([
                    _block('item', icon='🤝', title='Partner-Led Service',
                           body='A partner reviews every engagement. Nothing leaves our office without senior-level scrutiny.'),
                    _block('item', icon='📚', title='Always Current',
                           body='We continuously track regulatory changes so your filings are accurate and your planning is optimal.'),
                    _block('item', icon='🎯', title='Personal Attention',
                           body='You are not a number. We take time to understand your unique situation and goals.'),
                ]),
                services_intro='<p>From individual tax returns to complex corporate audits, '
                               'our experienced team delivers accurate, timely results.</p>',
                services=json.dumps([
                    _block('service', icon='📊', title='Tax Services',
                           body='Comprehensive tax preparation and planning for individuals, businesses, estates, and trusts.',
                           link_text='Learn more'),
                    _block('service', icon='🔍', title='Audit & Assurance',
                           body='Independent financial statement audits, reviews, and compilations that lenders and stakeholders trust.',
                           link_text='Learn more'),
                    _block('service', icon='💼', title='Business Advisory',
                           body='Strategic guidance on entity structure, cash flow, profitability, and growth planning.',
                           link_text='Learn more'),
                    _block('service', icon='🏛️', title='Estate & Trust',
                           body='Estate tax planning, trust administration, and fiduciary accounting to protect your legacy.',
                           link_text='Learn more'),
                    _block('service', icon='🏢', title='Corporate Tax',
                           body='Federal and multi-state corporate and partnership tax compliance and planning.',
                           link_text='Learn more'),
                    _block('service', icon='📈', title='Financial Reporting',
                           body='GAAP-compliant financial statements, bookkeeping support, and management reporting.',
                           link_text='Learn more'),
                ]),
                cta_headline='Ready to Get Started?',
                cta_body='<p>Whether you need a second opinion on your taxes, an audit for your business, '
                         'or long-term financial planning, we are here to help.</p>',
                cta_phone='(724) 555-0100',
            )
            root.add_child(instance=home)
            self.stdout.write(self.style.SUCCESS(f'  Created HomePage (id={home.pk})'))

        # ── Configure Wagtail Site ─────────────────────────────────────────────
        if not Site.objects.filter(is_default_site=True).exists():
            Site.objects.create(
                hostname='localhost',
                port=8000,
                root_page=home,
                is_default_site=True,
                site_name='BBA CPAs',
            )
            self.stdout.write(self.style.SUCCESS('  Created default Wagtail Site'))
        else:
            site = Site.objects.get(is_default_site=True)
            if site.root_page_id != home.pk:
                site.root_page = home
                site.save()

        # Helper: create a child page if it doesn't exist
        def create_child(PageClass, slug, **kwargs):
            existing = PageClass.objects.filter(slug=slug).first()
            if existing:
                self.stdout.write(f'  {PageClass.__name__} already exists (id={existing.pk})')
                return existing
            page = PageClass(slug=slug, **kwargs)
            home.add_child(instance=page)
            self.stdout.write(self.style.SUCCESS(f'  Created {PageClass.__name__} (id={page.pk})'))
            return page

        # ── AboutPage ─────────────────────────────────────────────────────────
        create_child(
            AboutPage, 'about',
            title='About BB&A',
            intro='<p>Brunner, Blackstone &amp; Associates, PC has been providing high-quality accounting '
                  'and advisory services to individuals, businesses, and estates for over 30 years. '
                  'We take the complexity of accounting and make it simple, so you can focus on '
                  'your business, your career, or your retirement.</p>',
            mission_statement='<p>To provide every client the highest level of professional service, '
                              'delivered with integrity, accuracy, and genuine personal care — '
                              'because your financial future deserves nothing less.</p>',
            body=json.dumps([]),
        )

        # ── ServicesPage ──────────────────────────────────────────────────────
        create_child(
            ServicesPage, 'services',
            title='Services',
            intro='<p>We offer a full suite of accounting, tax, and advisory services '
                  'tailored to meet the unique needs of each client. From simple individual '
                  'returns to complex multi-state corporate filings, our team has the expertise '
                  'to deliver accurate, timely results.</p>',
            services=json.dumps([
                _block('service', icon='📊', title='Tax Services',
                       body='Our tax professionals prepare federal, state, and local returns for individuals, '
                            'businesses, estates, and trusts. We also provide year-round tax planning to minimize '
                            'your liability and avoid surprises at filing time.',
                       link_text='Get in touch'),
                _block('service', icon='🔍', title='Audit & Assurance',
                       body='Our audit and assurance services provide independent verification of your financial '
                            'statements. We perform audits, reviews, and compilations in accordance with GAAP and '
                            'relevant professional standards.',
                       link_text='Get in touch'),
                _block('service', icon='💼', title='Business Advisory',
                       body='We help business owners make better decisions through financial analysis, budgeting, '
                            'forecasting, and strategic planning. From startup structuring to exit strategy, '
                            'we are your trusted advisor.',
                       link_text='Get in touch'),
                _block('service', icon='🏛️', title='Estate & Trust',
                       body='We work with individuals and families to develop estate plans that minimize taxes '
                            'and ensure a smooth transfer of wealth. Our trust accounting services provide '
                            'transparency and compliance for fiduciaries.',
                       link_text='Get in touch'),
                _block('service', icon='🏢', title='Corporate Tax',
                       body='From C-corporations and S-corporations to partnerships and LLCs, we handle '
                            'all forms of business entity tax compliance. We also assist with multi-state '
                            'filing obligations and nexus analysis.',
                       link_text='Get in touch'),
                _block('service', icon='📈', title='Financial Reporting',
                       body='Accurate financial statements are the foundation of sound business decisions. '
                            'We prepare GAAP-compliant financials, assist with bookkeeping, and provide '
                            'management reporting tailored to your needs.',
                       link_text='Get in touch'),
            ]),
        )

        # ── ResourceCenterPage ────────────────────────────────────────────────
        create_child(
            ResourceCenterPage, 'resource-center',
            title='Resource Center',
            intro='<p>We have assembled a collection of resources to help you stay informed '
                  'and organized throughout the year. Use the tools below to access important '
                  'forms, securely share files with our office, and more.</p>',
            tax_organizer_url='',
            irs_forms_url='https://www.irs.gov/forms-instructions',
            sharefile_url='https://bbacpas.sharefile.com',
            sharefile_signup_url='https://bbacpas.sharefile.com/register',
            resources=json.dumps([]),
        )

        # ── FinancialToolsPage ────────────────────────────────────────────────
        create_child(
            FinancialToolsPage, 'financial-tools',
            title='Financial Calculators',
            intro='<p>Use our suite of free financial calculators to help plan for retirement, '
                  'estimate your taxes, evaluate investments, and more. Results are for '
                  'illustrative purposes only — contact us for personalized advice.</p>',
        )

        # ── NewslettersPage ───────────────────────────────────────────────────
        create_child(
            NewslettersPage, 'newsletters',
            title='Tax Newsletters & Updates',
            intro='<p>Stay current with the latest tax law changes, planning opportunities, '
                  'and regulatory updates from our team of CPAs.</p>',
            newsletter_feed_url='',
            newsletters=json.dumps([]),
        )

        # ── LinksPage ─────────────────────────────────────────────────────────
        create_child(
            LinksPage, 'links',
            title='Helpful Links',
            intro='<p>We have compiled a list of websites that we have found to be helpful '
                  'resources for our clients. From IRS tools to secure file sharing, '
                  'these links are here to make your life easier.</p>',
            link_groups=json.dumps([
                _block('group',
                    group_title='Client Resources',
                    links=[
                        {'type': 'item', 'value': {'label': 'ShareFile Client Portal', 'url': 'https://bbacpas.sharefile.com', 'description': 'Secure client file portal'}},
                        {'type': 'item', 'value': {'label': 'Client Tax Organizer', 'url': '/resource-center/', 'description': 'Download your tax organizer'}},
                    ]
                ),
                _block('group',
                    group_title='IRS Resources',
                    links=[
                        {'type': 'item', 'value': {'label': 'Internal Revenue Service', 'url': 'https://www.irs.gov', 'description': 'Official IRS website'}},
                        {'type': 'item', 'value': {'label': 'Where Is My Refund?', 'url': 'https://www.irs.gov/refunds', 'description': 'Check your federal refund status'}},
                        {'type': 'item', 'value': {'label': 'IRS Forms & Publications', 'url': 'https://www.irs.gov/forms-instructions', 'description': 'Download any IRS form or publication'}},
                        {'type': 'item', 'value': {'label': 'Understanding IRS Notices', 'url': 'https://www.irs.gov/notices', 'description': 'Decode your IRS letter'}},
                        {'type': 'item', 'value': {'label': 'Identity Protection', 'url': 'https://www.irs.gov/identity-theft-fraud-scams', 'description': 'Prevention, detection, and victim assistance'}},
                        {'type': 'item', 'value': {'label': 'Report Phishing & Online Scams', 'url': 'https://www.irs.gov/privacy-disclosure/report-phishing', 'description': ''}},
                        {'type': 'item', 'value': {'label': "Can't Pay in Full?", 'url': 'https://www.irs.gov/payments/payment-plans-installment-agreements', 'description': 'IRS installment agreement options'}},
                        {'type': 'item', 'value': {'label': 'Check Amended Return Status', 'url': 'https://www.irs.gov/filing/wheres-my-amended-return', 'description': 'Track your Form 1040-X'}},
                    ]
                ),
                _block('group',
                    group_title='Government & Benefits',
                    links=[
                        {'type': 'item', 'value': {'label': 'Social Security Administration', 'url': 'https://www.ssa.gov', 'description': 'Benefits, statements, and planning'}},
                        {'type': 'item', 'value': {'label': 'EFTPS — Federal Tax Payments', 'url': 'https://www.eftps.gov', 'description': 'Electronic Federal Tax Payment System'}},
                        {'type': 'item', 'value': {'label': 'Energy Star', 'url': 'https://www.energystar.gov', 'description': 'Energy-efficient tax credit information'}},
                        {'type': 'item', 'value': {'label': 'PA myPATH (State Tax)', 'url': 'https://mypath.pa.gov', 'description': 'Pennsylvania state tax filing and payments'}},
                    ]
                ),
            ]),
        )

        # ── CareersPage ───────────────────────────────────────────────────────
        create_child(
            CareersPage, 'careers',
            title='Careers at BB&A',
            intro='<p>We are a client-focused firm committed to providing each and every client '
                  'the best service possible. We are looking for dedicated professionals who '
                  'share our commitment to excellence and personal service.</p>',
            culture_statement='<p>For self-starters who want to grow a great career '
                              'and enjoy the journey, BB&amp;A is the best of all worlds.</p>',
            benefits=json.dumps([
                _block('benefit', icon='⚖️', title='Work-Life Balance',
                       body='We respect your time outside the office and offer flexible scheduling, especially outside of tax season.'),
                _block('benefit', icon='📈', title='Career Growth',
                       body='We invest in our people through continuing education, mentorship, and a clear path to advancement.'),
                _block('benefit', icon='🤝', title='Collaborative Culture',
                       body='Work alongside experienced partners and colleagues who are generous with their knowledge.'),
                _block('benefit', icon='🏥', title='Competitive Benefits',
                       body='Health insurance, retirement plan, paid time off, and CPA exam support for qualifying staff.'),
                _block('benefit', icon='🎓', title='CPE & Development',
                       body='Firm-sponsored continuing professional education to keep your skills sharp and your license current.'),
                _block('benefit', icon='🏙️', title='Great Location',
                       body='Conveniently located with easy access and ample parking. No big-city commute headaches.'),
            ]),
            open_positions=json.dumps([]),
            apply_email='careers@bbacpas.com',
        )

        # ── ContactPage ───────────────────────────────────────────────────────
        create_child(
            ContactPage, 'contact',
            title='Contact Us',
            intro='<p>We would love to hear from you. Fill out the form below or reach us '
                  'directly by phone or email. Our team typically responds within one business day.</p>',
            address='1234 Main Street, Suite 100\nPittsburgh, PA 15222',
            phone='(724) 555-0100',
            email='info@bbacpas.com',
            hours='<p>Monday – Friday: 8:30 AM – 5:00 PM<br>Saturday: By appointment (tax season)<br>Sunday: Closed</p>',
            map_embed_url='',
        )

        self.stdout.write(self.style.SUCCESS('\nDone! Initial data loaded successfully.'))
        self.stdout.write('Next steps:')
        self.stdout.write('  1. Create a superuser: python manage.py createsuperuser')
        self.stdout.write('  2. Visit the CMS admin: http://localhost:8000/cms/')
        self.stdout.write('  3. Review and update page content as needed')
