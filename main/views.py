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
    # Get file data from Firebase Firestore
    file_data = get_file_from_firestore(path)
    
    if not file_data or 'data' not in file_data:
        raise Http404(f"File not found: {path}")
    
    # Decode base64 data
    try:
        decoded_data = base64.b64decode(file_data['data'])
    except Exception as e:
        return HttpResponse(f"Error decoding file: {str(e)}", status=500)
    
    # Create response with appropriate content type
    content_type = file_data.get('content_type', 'application/octet-stream')
    response = HttpResponse(decoded_data, content_type=content_type)
    
    # Add content disposition header for downloads if needed
    # response['Content-Disposition'] = f'inline; filename="{file_data.get("name", "file")}"'
    
    return response
