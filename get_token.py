#!/usr/bin/env python3
"""
Pinterest OAuth Helper
Helps you get an access token through browser-based OAuth flow
"""

import webbrowser
import http.server
import urllib.parse
import threading
import time
import os
from pathlib import Path

# Default values - you need to set these from your Pinterest App
# Go to: https://developers.pinterest.com/apps/
APP_ID = os.getenv('PINTEREST_APP_ID', '')
APP_SECRET = os.getenv('PINTEREST_APP_SECRET', '')
REDIRECT_URI = 'http://localhost:8888/callback'

# Scopes we need
SCOPES = [
    'boards:read',
    'pins:read', 
    'user_accounts:read',
]

authorization_code = None
server_running = True


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Handle OAuth callback"""
    
    def log_message(self, format, *args):
        pass  # Suppress logging
    
    def do_GET(self):
        global authorization_code, server_running
        
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if 'code' in params:
            authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'''
                <html>
                <head><title>Success!</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: green;">Authorization successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            ''')
            server_running = False
        elif 'error' in params:
            error = params.get('error', ['Unknown'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f'''
                <html>
                <head><title>Error</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: red;">Authorization failed</h1>
                    <p>Error: {error}</p>
                </body>
                </html>
            '''.encode())
            server_running = False
        else:
            self.send_response(404)
            self.end_headers()


def get_authorization_url():
    """Build Pinterest authorization URL"""
    params = {
        'client_id': APP_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ','.join(SCOPES),
    }
    base_url = 'https://www.pinterest.com/oauth/'
    return base_url + '?' + urllib.parse.urlencode(params)


def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token"""
    import httpx
    import base64
    
    # Create Basic Auth header
    credentials = f"{APP_ID}:{APP_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'continuous_refresh': 'true',  # Get refreshable token
    }
    
    response = httpx.post(
        'https://api.pinterest.com/v5/oauth/token',
        headers=headers,
        data=data,
    )
    
    return response.json()


def main():
    global authorization_code, server_running
    
    print("="*60)
    print("Pinterest OAuth Helper")
    print("="*60)
    
    # Check if we have app credentials
    if not APP_ID or not APP_SECRET:
        print("""
ERROR: App credentials not found!

You need to create a Pinterest App first:

1. Go to: https://developers.pinterest.com/apps/
2. Click "Create app" (or use existing app)
3. Fill in the required fields:
   - App name: (any name, e.g. "My Analytics")
   - Website: http://localhost (for testing)
   - Privacy Policy: http://localhost/privacy (for testing)
   - Purpose: Personal use / Analytics
   
4. After creating, go to app settings and copy:
   - App ID
   - App Secret

5. Add to your .env file or set environment variables:
   PINTEREST_APP_ID=your_app_id
   PINTEREST_APP_SECRET=your_app_secret

6. Run this script again.
""")
        return
    
    print(f"\nApp ID: {APP_ID[:8]}...")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Scopes: {', '.join(SCOPES)}")
    
    # Start local server
    print("\nStarting local OAuth callback server...")
    server = http.server.HTTPServer(('localhost', 8888), OAuthCallbackHandler)
    server_thread = threading.Thread(target=lambda: run_server(server))
    server_thread.start()
    
    # Open browser
    auth_url = get_authorization_url()
    print(f"\nOpening browser for authorization...")
    print(f"If browser doesn't open, visit: {auth_url}\n")
    webbrowser.open(auth_url)
    
    # Wait for callback
    print("Waiting for authorization...")
    while server_running:
        time.sleep(0.5)
    
    server.shutdown()
    server_thread.join()
    
    if not authorization_code:
        print("\nAuthorization failed or was cancelled.")
        return
    
    print(f"\nGot authorization code: {authorization_code[:20]}...")
    print("Exchanging for access token...")
    
    try:
        token_data = exchange_code_for_token(authorization_code)
        
        if 'access_token' in token_data:
            access_token = token_data['access_token']
            refresh_token = token_data.get('refresh_token', '')
            
            print("\n" + "="*60)
            print("SUCCESS! Your tokens:")
            print("="*60)
            print(f"\nAccess Token:\n{access_token}\n")
            if refresh_token:
                print(f"Refresh Token:\n{refresh_token}\n")
            
            # Save to .env
            env_path = Path(__file__).parent / '.env'
            print(f"Saving to {env_path}...")
            
            with open(env_path, 'w') as f:
                f.write(f"PINTEREST_APP_ID={APP_ID}\n")
                f.write(f"PINTEREST_APP_SECRET={APP_SECRET}\n")
                f.write(f"PINTEREST_ACCESS_TOKEN={access_token}\n")
                if refresh_token:
                    f.write(f"PINTEREST_REFRESH_TOKEN={refresh_token}\n")
            
            print("\nDone! You can now run: python main.py test")
            
        else:
            print(f"\nError getting token: {token_data}")
            
    except Exception as e:
        print(f"\nError exchanging code: {e}")


def run_server(server):
    """Run server until shutdown"""
    while server_running:
        server.handle_request()


if __name__ == '__main__':
    main()
