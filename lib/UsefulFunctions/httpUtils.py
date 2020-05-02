from wsgiref.util import FileWrapper
from django.http import FileResponse, HttpResponse

def getFileResponse(filedata, filename, filesize, contenttype, forcedownload=False):
    response = HttpResponse(filedata, content_type=contenttype) # Can also use write() function to create new "file"
    response['Content-Disposition'] = '%s; filename=%s' % ('attachment' if forcedownload else '', filename) # force browser to download file
    response['Content-Length'] = filesize
    return response
