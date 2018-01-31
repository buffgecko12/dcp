from django.http import HttpResponse

def getHttpFileResponse(filedata, filename, contentype):
    response = HttpResponse(filedata, content_type=contentype) # Can also use write() function to create new "file"
    response['Content-Disposition'] = 'attachment; filename=%s' % filename # force browser to download file
    return response