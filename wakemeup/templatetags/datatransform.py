from django import template
from lib.UsefulFunctions.dateUtils import parse_timestamp
register = template.Library()

# Return ISO time as datetime object
@register.filter(expects_localtime=True)
def parse_date(value):
    return parse_timestamp(value)
