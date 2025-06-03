from django.http import HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_control
import base64

from .firebase_firestore_config import get_file_from_firestore

def health_check(request):
    """
    Simple health check endpoint to verify the application is running.
    """
    return HttpResponse("OK")

@require_http_methods(["GET"])
@cache_control(max_age=86400, public=True)  # Cache for 24 hours
def serve_media_file(request, path):
    """
    Serve media files from Firebase Firestore.
    This view retrieves files stored as base64-encoded strings in Firestore documents
    and serves them with the appropriate content type.
    """
    try:
        # Get file data from Firebase Firestore
        file_data = get_file_from_firestore(path)
        
        if not file_data:
            # Return a default image or placeholder if available
            # For now, just raise a 404
            raise Http404(f"File not found: {path}")
        
        if 'data' not in file_data:
            return HttpResponse(f"Invalid file data format for: {path}", status=500)
        
        # Decode base64 data
        try:
            decoded_data = base64.b64decode(file_data['data'])
        except Exception as e:
            return HttpResponse(f"Error decoding file: {str(e)}", status=500)
        
        # Create response with appropriate content type
        content_type = file_data.get('content_type', 'application/octet-stream')
        response = HttpResponse(decoded_data, content_type=content_type)
        
        # Add cache headers
        response['Cache-Control'] = 'public, max-age=86400'  # 24 hours
        
        # Add content disposition header for downloads if needed
        # response['Content-Disposition'] = f'inline; filename="{file_data.get("name", "file")}"'
        
        return response
    except Exception as e:
        print(f"Error serving media file {path}: {str(e)}")
        return HttpResponse(f"Server error: Unable to retrieve file", status=500)
