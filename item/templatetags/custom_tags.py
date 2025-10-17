from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Позволяет обращаться к словарям в шаблоне"""
    try:
        return d.get(int(key)) or d.get(str(key)) or 0
    except Exception:
        return 0
