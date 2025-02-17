from django import template

register = template.Library()

@register.filter
def split_and_join(value):
    if isinstance(value, str):
        # Split the string by commas, remove extra spaces, then join with commas and spaces
        return ", ".join([v.strip() for v in value.split(",")])
    return value
