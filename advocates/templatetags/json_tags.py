from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def json_script(value, element_id):
    """Output a Python object as JSON in a <script> tag with the given ID."""
    json_str = json.dumps(value)
    return mark_safe(f'<script id="{element_id}" type="application/json">{json_str}</script>')