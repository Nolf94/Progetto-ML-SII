from django import template

register = template.Library()

@register.filter
def keyvalue(dict, key):
    try:
        return dict.get(key,'')
    except (KeyError, TypeError):
        return ''
