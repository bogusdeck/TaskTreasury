"""
Simplified WSGI config for main project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Handle the missing distutils module
try:
    import distutils.version
except ImportError:
    # If distutils is not available, create a fake module
    import distutils_patch
    
    # Create a fake distutils module structure
    class VersionModule:
        LooseVersion = distutils_patch.LooseVersion
    
    class DistutilsModule:
        version = VersionModule
    
    # Add it to sys.modules
    sys.modules['distutils'] = DistutilsModule
    sys.modules['distutils.version'] = VersionModule

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.vercel_settings')

# Create a WSGI application with error handling
def application(environ, start_response):
    try:
        # Import Django and initialize it
        from django.core.wsgi import get_wsgi_application
        django_app = get_wsgi_application()
        
        # Forward the request to Django
        return django_app(environ, start_response)
    except Exception as e:
        # If there's an error, return a 500 response with details
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TaskTreasury - Error</title>
            <link href="https://fonts.googleapis.com/css2?family=Cascadia+Code:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Cascadia Code', monospace;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem;
                    line-height: 1.6;
                }}
                h1 {{
                    color: #dc2626;
                }}
                .error {{
                    background-color: #fee2e2;
                    border-left: 4px solid #dc2626;
                    padding: 1rem;
                    margin: 1rem 0;
                    overflow-x: auto;
                }}
                pre {{
                    white-space: pre-wrap;
                }}
            </style>
        </head>
        <body>
            <h1>Application Error</h1>
            <div class="error">
                <p>An error occurred while processing your request:</p>
                <pre>{str(e)}</pre>
            </div>
        </body>
        </html>
        """
        
        return [error_html.encode('utf-8')]

# Export the application for Vercel
application = application

# Vercel looks for 'app' or 'handler' variable
app = application
