from django.template import Library

register = Library()


@register.filter
def times(value):
    try:
        value = int(value)
    except:
        return []
    return range(value)
