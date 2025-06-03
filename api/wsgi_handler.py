"""
Vercel handler for Django WSGI application.
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
    sys.path.insert(0, project_root)
    
    # Create a custom LooseVersion class
    class LooseVersion:
        def __init__(self, vstring=None):
            self.parse(vstring)
            
        def parse(self, vstring):
            if vstring is None:
                self.vstring = ""
            else:
                self.vstring = str(vstring)
                
            components = []
            for component in self.vstring.split('.'):
                try:
                    components.append(int(component))
                except ValueError:
                    components.append(component)
            self.version = components
            
        def __str__(self):
            return self.vstring
            
        def __repr__(self):
            return f"LooseVersion('{self.vstring}')"
            
        def __eq__(self, other):
            if isinstance(other, str):
                other = LooseVersion(other)
            return self.version == other.version
            
        def __lt__(self, other):
            if isinstance(other, str):
                other = LooseVersion(other)
            
            # Compare version components
            for i, component in enumerate(self.version):
                if i >= len(other.version):
                    # If self has more components and all previous components were equal, self is greater
                    return False
                    
                # If components are different types (str vs int), convert to str for comparison
                if type(component) != type(other.version[i]):
                    if component < str(other.version[i]):
                        return True
                    elif component > str(other.version[i]):
                        return False
                else:
                    if component < other.version[i]:
                        return True
                    elif component > other.version[i]:
                        return False
                        
            # If we get here and other has more components, self is less
            return len(self.version) < len(other.version)
    
    # Create fake modules
    class VersionModule:
        LooseVersion = LooseVersion
    
    class DistutilsModule:
        version = VersionModule
    
    # Add to sys.modules
    sys.modules['distutils'] = DistutilsModule
    sys.modules['distutils.version'] = VersionModule

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.vercel_settings')

# Create a handler function for Vercel
def handler(event, context):
    """
    Handler function for Vercel serverless function.
    """
    try:
        # Import Django and initialize it
        from django.core.wsgi import get_wsgi_application
        from django.core.handlers.wsgi import WSGIHandler
        
        # Create a Django WSGI handler
        django_app = get_wsgi_application()
        
        # Convert the event to WSGI format
        method = event.get('method', 'GET')
        path = event.get('path', '/')
        query_string = event.get('query', '')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Create a WSGI environment
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'CONTENT_LENGTH': str(len(body)),
            'CONTENT_TYPE': headers.get('content-type', ''),
            'wsgi.input': body,
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'https',
        }
        
        # Add HTTP headers
        for key, value in headers.items():
            environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
        
        # Call the Django application
        response_body = []
        status_headers = []
        
        def start_response(status, headers):
            status_headers.append((status, headers))
            return response_body.append
        
        response = django_app(environ, start_response)
        
        # Get the response
        if response_body:
            body = response_body[0]
        else:
            body = b''.join(response)
        
        status, headers = status_headers[0]
        status_code = int(status.split(' ')[0])
        
        # Convert headers to dict
        headers_dict = {}
        for key, value in headers:
            headers_dict[key] = value
        
        # Return the response
        return {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': body.decode('utf-8') if isinstance(body, bytes) else body
        }
    except Exception as e:
        # Return an error response
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f"""
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
        }
