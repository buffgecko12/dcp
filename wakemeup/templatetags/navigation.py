from django import template
register = template.Library()

def add_linkpost_fields(fields, navcontext, formname):
    fields.update(navcontext.setdefault('link_post', {}).setdefault(formname, {}).get('fields', {}))

@register.inclusion_tag('link_post.html')
def link_post(navcontext, formname, actionurl, displaytype, urlname, linktext, formurlname=None, **kwargs):

    # Set default value
    if not formurlname:
        formurlname = formname
    
    fields = {}

    # Add link_post fields
    add_linkpost_fields(fields, navcontext, formname)

    # Add additional fields    
    if formname == "execute_admintools":
        fields.update({'action':'drivesync'})
    elif formname == "edit_permissions":
        fields.update({'permissiontype': kwargs.get("permissiontype", None)})
                
    return {
        'formname':formname,
        'formurlname':formurlname,
        'actionurl':actionurl,
        'displaytype':displaytype,
        'urlname':urlname,
        'linktext':linktext,
        'fields': fields,
    }
