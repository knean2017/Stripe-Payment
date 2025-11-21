"""
Vercel serverless function handler for Django application.
This file wraps the Django WSGI application to work with Vercel's serverless environment.
"""

import os
import sys
from pathlib import Path
from io import BytesIO

# Add the proj directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
PROJ_DIR = BASE_DIR / "proj"
sys.path.insert(0, str(PROJ_DIR))

# Set Vercel environment variable
os.environ["VERCEL"] = "1"

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Get the WSGI application
application = get_wsgi_application()

# Vercel serverless function handler
# Vercel's Python runtime calls this handler function with a request object
def handler(request):
    """
    Vercel serverless function handler.
    This function is called by Vercel for each HTTP request.
    
    Args:
        request: Vercel request object (dict-like) with:
            - method: HTTP method (GET, POST, etc.)
            - path: Request path
            - headers: Dict of HTTP headers
            - body: Request body (string or bytes)
            - queryStringParameters: Dict of query parameters
    
    Returns:
        dict: Response dictionary with:
            - statusCode: HTTP status code
            - headers: Dict of response headers
            - body: Response body string
    """
    from django.core.handlers.wsgi import WSGIHandler
    
    # Extract request information (handle both dict and object-like access)
    if isinstance(request, dict):
        method = request.get('method', 'GET')
        path = request.get('path', '/')
        headers = request.get('headers', {})
        body = request.get('body', '')
        query_string = request.get('queryStringParameters', {}) or {}
    else:
        # Handle object-like access (if Vercel passes an object)
        method = getattr(request, 'method', 'GET')
        path = getattr(request, 'path', '/')
        headers = getattr(request, 'headers', {})
        body = getattr(request, 'body', '')
        query_string = getattr(request, 'queryStringParameters', {}) or {}
    
    # Build query string
    if query_string:
        qs = '&'.join([f"{k}={v}" for k, v in query_string.items()])
    else:
        qs = ''
    
    # Convert body to bytes if it's a string
    if isinstance(body, str):
        body_bytes = body.encode('utf-8')
    else:
        body_bytes = body if body else b''
    
    # Extract host from headers
    host = headers.get('host', 'localhost')
    if isinstance(host, str):
        server_name = host.split(':')[0]
        server_port = host.split(':')[1] if ':' in host else '80'
    else:
        server_name = 'localhost'
        server_port = '80'
    
    # Convert Vercel request to WSGI environ format
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': qs,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body_bytes)),
        'SERVER_NAME': server_name,
        'SERVER_PORT': server_port,
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https' if headers.get('x-forwarded-proto') == 'https' else 'http',
        'wsgi.input': BytesIO(body_bytes),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add all headers to environ (WSGI format: HTTP_ prefix)
    for key, value in headers.items():
        if isinstance(key, str) and isinstance(value, str):
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key}'] = value
    
    # Create WSGI handler
    wsgi_handler = WSGIHandler()
    
    # Response data collector
    response_status = []
    response_headers = []
    
    def start_response(status, headers_list):
        """WSGI start_response callback"""
        response_status.append(status)
        response_headers.extend(headers_list)
    
    # Process request through Django
    try:
        response_body = wsgi_handler(environ, start_response)
        
        # Extract status code
        status_code = int(response_status[0].split()[0]) if response_status else 200
        
        # Convert headers to dict (WSGI headers are list of tuples)
        response_headers_dict = {}
        for header in response_headers:
            if isinstance(header, (tuple, list)) and len(header) == 2:
                response_headers_dict[header[0]] = header[1]
        
        # Collect response body
        body_parts = []
        for part in response_body:
            if isinstance(part, bytes):
                body_parts.append(part)
            else:
                body_parts.append(str(part).encode('utf-8'))
        
        response_body_str = b''.join(body_parts).decode('utf-8')
        
        return {
            'statusCode': status_code,
            'headers': response_headers_dict,
            'body': response_body_str
        }
    except Exception as e:
        # Error handling - return 500 error
        import traceback
        from django.conf import settings
        error_msg = str(e)
        if settings.DEBUG:
            error_msg += '\n' + traceback.format_exc()
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Internal Server Error: {error_msg}'
        }

