from django.http import FileResponse

def getFileResponse(filedata, filename, filesize, contenttype):
    response = FileResponse(filedata, content_type=contenttype) # Can also use write() function to create new "file"
    response['Content-Disposition'] = 'attachment; filename=%s' % filename # force browser to download file
    response['Content-Length'] = filesize
    return response