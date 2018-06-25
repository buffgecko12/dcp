from PIL import Image
import io
from django.http import HttpResponse

def renderImageFromDb(blob):
    im = createThumbnailFromDb(blob)

    # serialize to HTTP response    
    response = HttpResponse(content_type="image/png")
    im.save(response, "PNG")    
    return response

def createThumbnailFromDb(blob):
    img = Image.open(io.BytesIO(blob))
    img.thumbnail((200, 200), Image.ANTIALIAS)
    return img