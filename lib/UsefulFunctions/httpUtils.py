from wsgiref.util import FileWrapper
from django.http import FileResponse, HttpResponse

def getFileResponse(filedata, filename, filesize, contenttype, forcedownload=False):
    response = HttpResponse(filedata, content_type=contenttype) # Can also use write() function to create new "file"
    response['Content-Disposition'] = '%s; filename=%s' % ('attachment' if forcedownload else '', filename) # force browser to download file
    response['Content-Length'] = filesize
    return response

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
def get_mimetype(fileformat):
    myformat = None

    if fileformat:
        # Export (https://developers.google.com/drive/api/v3/ref-export-formats)
        if fileformat == "docx":
            myformat = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif fileformat == "pdf":
            myformat = 'application/pdf'
            
        # Google (https://developers.google.com/drive/api/v3/mime-types)            
        elif fileformat == "gdoc":
            myformat = 'application/vnd.google-apps.document'

    return myformat
