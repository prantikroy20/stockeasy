from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Multiplies the value by the argument
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def count_active(suppliers):
    """
    Counts the number of active suppliers in a queryset
    """
    return sum(1 for supplier in suppliers if supplier.is_active)

@register.filter
def sum_attr(objects, attr_name):
    """
    Sums the values of a specific attribute across all objects in a queryset
    """
    total = 0
    for obj in objects:
        try:
            value = getattr(obj, attr_name, 0)
            if value is not None:
                total += value
        except (ValueError, TypeError):
            pass
    return total