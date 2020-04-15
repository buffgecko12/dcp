from wsgiref.util import FileWrapper
from django.http import FileResponse, HttpResponse

def getFileResponse(filedata, filename, filesize, contenttype):
    response = HttpResponse(filedata, content_type=contenttype) # Can also use write() function to create new "file"
    response['Content-Disposition'] = 'attachment; filename=%s' % filename # force browser to download file
    response['Content-Length'] = filesize
    return response