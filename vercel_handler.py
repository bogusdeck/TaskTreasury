from http.server import BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TaskTreasury</title>
            <style>
                body {
                    font-family: 'Cascadia Code', monospace;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem;
                    line-height: 1.6;
                }
                h1 {
                    color: #4f46e5;
                }
                .message {
                    background-color: #f3f4f6;
                    border-left: 4px solid #4f46e5;
                    padding: 1rem;
                    margin: 1rem 0;
                }
                .button {
                    display: inline-block;
                    background-color: #4f46e5;
                    color: white;
                    padding: 0.5rem 1rem;
                    text-decoration: none;
                    border-radius: 0.25rem;
                    margin-top: 1rem;
                }
            </style>
        </head>
        <body>
            <h1>TaskTreasury</h1>
            <div class="message">
                <p>We're currently experiencing technical difficulties with our deployment.</p>
                <p>Our team is working to resolve this issue as quickly as possible.</p>
                <p>Please check back soon!</p>
            </div>
            <a href="mailto:support@tasktreasury.com" class="button">Contact Support</a>
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode('utf-8'))
        return

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TaskTreasury</title>
            <style>
                body {
                    font-family: 'Cascadia Code', monospace;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem;
                    line-height: 1.6;
                }
                h1 {
                    color: #4f46e5;
                }
                .message {
                    background-color: #f3f4f6;
                    border-left: 4px solid #4f46e5;
                    padding: 1rem;
                    margin: 1rem 0;
                }
                .button {
                    display: inline-block;
                    background-color: #4f46e5;
                    color: white;
                    padding: 0.5rem 1rem;
                    text-decoration: none;
                    border-radius: 0.25rem;
                    margin-top: 1rem;
                }
            </style>
        </head>
        <body>
            <h1>TaskTreasury</h1>
            <div class="message">
                <p>We're currently experiencing technical difficulties with our deployment.</p>
                <p>Our team is working to resolve this issue as quickly as possible.</p>
                <p>Please check back soon!</p>
            </div>
            <a href="mailto:support@tasktreasury.com" class="button">Contact Support</a>
        </body>
        </html>
        """
    }
