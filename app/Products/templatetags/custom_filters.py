# app/Products/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def space_format(value):
    return "{:,}".format(int(value)).replace(",", " ")