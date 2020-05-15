from django import template
import datetime

register = template.Library()

# Return ISO time as datetime object
@register.filter(expects_localtime=True)
def parse_date(value):
    mydate = None
    format = "%Y-%m-%d"

    if value:
        try:
            mydate = datetime.datetime.strptime(value, format)
        except:
            mydate = datetime.datetime.strptime(value, format + "T%H:%M:%SZ")
        
    return mydate