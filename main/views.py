from django.http import JsonResponse

def health_check(request):
    """
    Simple health check endpoint to verify the application is running
    """
    return JsonResponse({
        "status": "ok",
        "message": "TaskTreasury API is running"
    })
