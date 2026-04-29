from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    DateBlock,
    ListBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.images.blocks import ImageChooserBlock


class ServiceBlock(StructBlock):
    icon = CharBlock(help_text='Emoji or icon character')
    title = CharBlock()
    body = TextBlock()
    link_text = CharBlock(default='Learn more')

    class Meta:
        icon = 'list-ul'
        label = 'Service'


class WhyItemBlock(StructBlock):
    icon = CharBlock(help_text='Emoji or icon character')
    title = CharBlock()
    body = TextBlock()

    class Meta:
        icon = 'tick'
        label = 'Why BBA Item'


class TeamMemberBlock(StructBlock):
    initials = CharBlock(max_length=3)
    name = CharBlock()
    title = CharBlock()
    bio = TextBlock()
    photo = ImageChooserBlock(required=False)

    class Meta:
        icon = 'user'
        label = 'Team Member'


class HighlightBlock(StructBlock):
    text = RichTextBlock()
    style = ChoiceBlock(
        choices=[
            ('navy', 'Navy background'),
            ('gold', 'Gold accent'),
            ('plain', 'Plain'),
        ],
        default='plain',
    )

    class Meta:
        icon = 'pick'
        label = 'Highlight Block'


class ResourceItemBlock(StructBlock):
    icon = CharBlock(help_text='Emoji or icon character')
    title = CharBlock()
    description = TextBlock()
    link_text = CharBlock(default='Access')
    link_url = URLBlock()
    external = BooleanBlock(default=True, required=False)

    class Meta:
        icon = 'link'
        label = 'Resource Item'


class NewsletterItemBlock(StructBlock):
    title = CharBlock()
    date = DateBlock()
    excerpt = TextBlock()
    url = URLBlock()

    class Meta:
        icon = 'doc-full'
        label = 'Newsletter'


class LinkItemBlock(StructBlock):
    label = CharBlock()
    url = URLBlock()
    description = CharBlock(required=False)

    class Meta:
        icon = 'link'
        label = 'Link'


class LinkGroupBlock(StructBlock):
    group_title = CharBlock()
    links = ListBlock(LinkItemBlock())

    class Meta:
        icon = 'list-ul'
        label = 'Link Group'


class BenefitBlock(StructBlock):
    icon = CharBlock(help_text='Emoji or icon character')
    title = CharBlock()
    body = TextBlock()

    class Meta:
        icon = 'tick-inverse'
        label = 'Benefit'


class JobPositionBlock(StructBlock):
    title = CharBlock()
    type = ChoiceBlock(
        choices=[
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('seasonal', 'Seasonal'),
        ]
    )
    description = RichTextBlock()
    requirements = RichTextBlock()

    class Meta:
        icon = 'form'
        label = 'Job Position'
