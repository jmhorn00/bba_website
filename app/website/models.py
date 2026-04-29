import logging

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

logger = logging.getLogger(__name__)

from .blocks import (
    BenefitBlock,
    HighlightBlock,
    JobPositionBlock,
    LinkGroupBlock,
    NewsletterItemBlock,
    ResourceItemBlock,
    ServiceBlock,
    TeamMemberBlock,
    WhyItemBlock,
)


class HomePage(Page):
    max_count = 1

    # Hero
    hero_headline = models.CharField(max_length=200, default='Precision. Integrity. Results.')
    hero_subheadline = RichTextField(default='')
    hero_cta_text = models.CharField(max_length=60, default='Schedule a Consultation')
    hero_stat_1_number = models.CharField(max_length=20, default='30+')
    hero_stat_1_label = models.CharField(max_length=60, default='Years of Experience')
    hero_stat_2_number = models.CharField(max_length=20, default='500+')
    hero_stat_2_label = models.CharField(max_length=60, default='Clients Served')
    hero_stat_3_number = models.CharField(max_length=20, default='50')
    hero_stat_3_label = models.CharField(max_length=60, default='States Served')

    # Why BBA
    why_headline = models.CharField(max_length=200, default='Why Choose BB&A?')
    why_body = RichTextField(default='')
    why_items = StreamField([('item', WhyItemBlock())], blank=True, use_json_field=True)

    # Services
    services_intro = RichTextField(default='')
    services = StreamField([('service', ServiceBlock())], blank=True, use_json_field=True)

    # Team
    team_members = StreamField([('member', TeamMemberBlock())], blank=True, use_json_field=True)

    # CTA Banner
    cta_headline = models.CharField(max_length=200, default='Ready to Get Started?')
    cta_body = RichTextField(default='')
    cta_phone = models.CharField(max_length=30, default='(724) 555-0100')

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_headline'),
            FieldPanel('hero_subheadline'),
            FieldPanel('hero_cta_text'),
            MultiFieldPanel([
                FieldPanel('hero_stat_1_number'),
                FieldPanel('hero_stat_1_label'),
            ], heading='Stat 1'),
            MultiFieldPanel([
                FieldPanel('hero_stat_2_number'),
                FieldPanel('hero_stat_2_label'),
            ], heading='Stat 2'),
            MultiFieldPanel([
                FieldPanel('hero_stat_3_number'),
                FieldPanel('hero_stat_3_label'),
            ], heading='Stat 3'),
        ], heading='Hero Section'),
        MultiFieldPanel([
            FieldPanel('why_headline'),
            FieldPanel('why_body'),
            FieldPanel('why_items'),
        ], heading='Why BBA Section'),
        MultiFieldPanel([
            FieldPanel('services_intro'),
            FieldPanel('services'),
        ], heading='Services Section'),
        FieldPanel('team_members'),
        MultiFieldPanel([
            FieldPanel('cta_headline'),
            FieldPanel('cta_body'),
            FieldPanel('cta_phone'),
        ], heading='CTA Banner'),
    ]

    class Meta:
        verbose_name = 'Home Page'


class AboutPage(Page):
    max_count = 1

    intro = RichTextField()
    mission_statement = RichTextField()
    body = StreamField([
        ('paragraph', RichTextField()),
        ('highlight', HighlightBlock()),
        ('team_member', TeamMemberBlock()),
    ], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('mission_statement'),
        FieldPanel('body'),
    ]

    class Meta:
        verbose_name = 'About Page'


class ServicesPage(Page):
    max_count = 1

    intro = RichTextField()
    services = StreamField([('service', ServiceBlock())], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('services'),
    ]

    class Meta:
        verbose_name = 'Services Page'


class ResourceCenterPage(Page):
    max_count = 1

    intro = RichTextField()
    tax_organizer_url = models.URLField(
        blank=True,
        help_text='Link to downloadable tax organizer PDF',
    )
    irs_forms_url = models.URLField(
        default='https://www.irs.gov/forms-instructions',
        help_text='Link to IRS forms library',
    )
    sharefile_url = models.URLField(
        default='https://bbacpas.sharefile.com',
        help_text='ShareFile portal login URL',
    )
    sharefile_signup_url = models.URLField(
        default='https://bbacpas.sharefile.com/register',
        help_text='ShareFile new account URL',
    )
    resources = StreamField([('resource', ResourceItemBlock())], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        MultiFieldPanel([
            FieldPanel('tax_organizer_url'),
            FieldPanel('irs_forms_url'),
            FieldPanel('sharefile_url'),
            FieldPanel('sharefile_signup_url'),
        ], heading='Resource URLs'),
        FieldPanel('resources'),
    ]

    class Meta:
        verbose_name = 'Resource Center Page'


class FinancialToolsPage(Page):
    max_count = 1

    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request, *args, **kwargs):
        from calculators.registry import CALCULATORS
        ctx = super().get_context(request, *args, **kwargs)
        ctx['calculators'] = CALCULATORS
        return ctx

    class Meta:
        verbose_name = 'Financial Tools Page'


class NewslettersPage(Page):
    max_count = 1

    intro = RichTextField()
    newsletter_feed_url = models.URLField(
        blank=True,
        help_text='RSS/JSON feed URL from newsletter provider (e.g. Thomson Reuters Checkpoint). Leave blank to use manually-entered items.',
    )
    newsletters = StreamField([('newsletter', NewsletterItemBlock())], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('newsletter_feed_url'),
        FieldPanel('newsletters'),
    ]

    def _fetch_feed(self):
        cached = cache.get('newsletter_feed')
        if cached is not None:
            return cached
        try:
            import xml.etree.ElementTree as ET
            from email.utils import parsedate_to_datetime

            resp = requests.get(self.newsletter_feed_url, timeout=5)
            resp.raise_for_status()
            items = []
            root = ET.fromstring(resp.text)
            for item in root.iter('item'):
                title = item.findtext('title', '')
                link = item.findtext('link', '')
                desc = item.findtext('description', '')
                pub = item.findtext('pubDate', '')
                try:
                    pub_date = parsedate_to_datetime(pub).date() if pub else None
                except Exception:
                    pub_date = None
                items.append({'title': title, 'url': link, 'excerpt': desc[:200], 'date': pub_date})
            cache.set('newsletter_feed', items, settings.CACHE_TIMEOUT)
            return items
        except Exception:
            logger.warning('Failed to fetch newsletter feed from %s', self.newsletter_feed_url)
            return None

    def _normalize_blocks(self):
        return [
            {
                'title': b.value['title'],
                'date': b.value['date'],
                'excerpt': b.value['excerpt'],
                'url': b.value['url'],
            }
            for b in self.newsletters
        ]

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        if self.newsletter_feed_url:
            feed_items = self._fetch_feed()
            items = feed_items if feed_items else self._normalize_blocks()
        else:
            items = self._normalize_blocks()

        paginator = Paginator(items, 10)
        page_num = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_num)

        ctx['newsletters'] = page_obj
        ctx['is_paginated'] = paginator.num_pages > 1
        ctx['page_obj'] = page_obj
        return ctx

    class Meta:
        verbose_name = 'Newsletters Page'


class LinksPage(Page):
    max_count = 1

    intro = RichTextField()
    link_groups = StreamField([('group', LinkGroupBlock())], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('link_groups'),
    ]

    class Meta:
        verbose_name = 'Links Page'


class CareersPage(Page):
    max_count = 1

    intro = RichTextField()
    culture_statement = RichTextField()
    benefits = StreamField([('benefit', BenefitBlock())], blank=True, use_json_field=True)
    open_positions = StreamField([('position', JobPositionBlock())], blank=True, use_json_field=True)
    apply_email = models.EmailField(default='careers@bbacpas.com')

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('culture_statement'),
        FieldPanel('benefits'),
        FieldPanel('open_positions'),
        FieldPanel('apply_email'),
    ]

    class Meta:
        verbose_name = 'Careers Page'


class ContactPage(Page):
    max_count = 1

    intro = RichTextField()
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    hours = RichTextField()
    map_embed_url = models.URLField(blank=True, help_text='Google Maps embed URL (iframe src)')

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        MultiFieldPanel([
            FieldPanel('address'),
            FieldPanel('phone'),
            FieldPanel('email'),
            FieldPanel('hours'),
            FieldPanel('map_embed_url'),
        ], heading='Contact Details'),
    ]

    class Meta:
        verbose_name = 'Contact Page'
