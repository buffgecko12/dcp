from django import template
register = template.Library()

@register.inclusion_tag('link_post.html')
def link_post(navcontext, formname, actionurl, displaytype, urlname, linktext, formurlname=None):

    # Set default value
    if not formurlname:
        formurlname = formname
    
    fields = {}
    
    if formname == 'upload_file':
        fields.update(navcontext.setdefault('link_post', {}).setdefault(formname, {}).get('fields', {}))
    elif formname == "execute_admintools":
        fields.update({'action':'drivesync'})

    return {
        'formname':formname,
        'formurlname':formurlname,
        'actionurl':actionurl,
        'displaytype':displaytype,
        'urlname':urlname,
        'linktext':linktext,
        'fields': fields,
    }
