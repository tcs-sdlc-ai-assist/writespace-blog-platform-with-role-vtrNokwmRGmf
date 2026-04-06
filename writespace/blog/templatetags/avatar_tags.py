from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def render_avatar(user):
    if user.is_staff:
        emoji = '👑'
        bg_class = 'background-color: #7c3aed;'
    else:
        emoji = '📖'
        bg_class = 'background-color: #2563eb;'

    display_name = user.first_name or user.username

    return format_html(
        '<span style="display: inline-flex; align-items: center; gap: 0.5rem; '
        'padding: 0.25rem 0.75rem; border-radius: 9999px; color: white; '
        'font-size: 0.875rem; font-weight: 500; {bg_class}">'
        '<span>{emoji}</span>'
        '<span>{display_name}</span>'
        '</span>',
        bg_class=bg_class,
        emoji=emoji,
        display_name=display_name,
    )