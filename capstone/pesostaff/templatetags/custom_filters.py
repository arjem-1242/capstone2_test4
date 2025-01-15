from django import template

register = template.Library()

@register.filter
def get_field(instance, file_field):
    return getattr(instance, file_field, None)