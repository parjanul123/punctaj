"""
OAuth Callback Handler
Simple local HTTP server to handle OAuth redirects
Useful for testing OAuth flows locally
"""

import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from banks"""
    
    # Class variable to store the auth code
    auth_code = None
    
    def do_GET(self):
        """Handle GET request from OAuth redirect"""
        try:
            # Parse the URL
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Extract authorization code
            if 'code' in query_params:
                OAuthCallbackHandler.auth_code = query_params['code'][0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = """
                <html>
                <head>
                    <title>✅ Authorization Successful</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .success { color: green; font-size: 24px; }
                        .code { background: #f0f0f0; padding: 20px; border-radius: 5px; font-family: monospace; margin: 20px 0; }
                    </style>
                </head>
                <body>
                    <h1 class="success">✅ Authorization Successful!</h1>
                    <p>You can now close this window and return to Punctaj Manager.</p>
                    <p>Your authorization code has been captured.</p>
                    <div class="code">""" + OAuthCallbackHandler.auth_code + """</div>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
                logger.info("✅ Authorization code received successfully")
                
            elif 'error' in query_params:
                error = query_params['error'][0]
                error_desc = query_params.get('error_description', ['Unknown error'])[0]
                
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = f"""
                <html>
                <head>
                    <title>❌ Authorization Failed</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                        .error {{ color: red; font-size: 20px; }}
                    </style>
                </head>
                <body>
                    <h1 class="error">❌ Authorization Failed</h1>
                    <p>Error: {error}</p>
                    <p>Description: {error_desc}</p>
                    <p>Please try again.</p>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
                logger.error(f"❌ Authorization error: {error} - {error_desc}")
            
            else:
                # No code or error
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = """
                <html>
                <head>
                    <title>❌ Invalid Request</title>
                </head>
                <body>
                    <h1>❌ Invalid OAuth Callback</h1>
                    <p>No authorization code or error found in callback.</p>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
                logger.error("❌ Invalid OAuth callback - no code or error")
        
        except Exception as e:
            logger.error(f"❌ Error handling OAuth callback: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"<h1>500 Internal Server Error</h1>")
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging"""
        logger.debug(f"OAuth Server: {format % args}")


class OAuthCallbackServer:
    """Simple OAuth callback server"""
    
    def __init__(self, port: int = 8080):
        """
        Initialize OAuth callback server
        
        Args:
            port: Port to listen on (default: 8080)
        """
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the callback server"""
        try:
            self.server = HTTPServer(('localhost', self.port), OAuthCallbackHandler)
            
            def run_server():
                logger.info(f"🟢 OAuth callback server started on http://localhost:{self.port}")
                self.server.handle_request()  # Handle one request only
                logger.info("🟢 OAuth callback server stopped")
            
            self.thread = threading.Thread(target=run_server, daemon=True)
            self.thread.start()
            logger.info(f"✅ OAuth callback server listening on port {self.port}")
            
        except Exception as e:
            logger.error(f"❌ Error starting OAuth callback server: {e}")
    
    def stop(self):
        """Stop the callback server"""
        try:
            if self.server:
                self.server.shutdown()
                self.server = None
            logger.info("✅ OAuth callback server stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping OAuth callback server: {e}")
    
    def get_auth_code(self) -> str:
        """
        Get the received authorization code
        
        Returns:
            Authorization code if received, None otherwise
        """
        return OAuthCallbackHandler.auth_code
    
    def reset_auth_code(self):
        """Reset the stored auth code"""
        OAuthCallbackHandler.auth_code = None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start server
    server = OAuthCallbackServer(port=8080)
    server.start()
    
    # Simulate opening auth URL
    print("\n✅ OAuth Callback Server started on http://localhost:8080")
    print("📋 Waiting for authorization code...\n")
    
    # In a real scenario, the user would visit the auth URL and be redirected here
    # For now, we'll just wait for testing
    import time
    
    # Open browser with a test URL (this won't work, just for demo)
    # webbrowser.open("http://localhost:8080/callback?code=test_code_12345")
    
    # Wait for callback
    print("💡 Tip: Open this URL in your browser:")
    print("   http://localhost:8080/callback?code=TEST_AUTH_CODE")
    print("\n⏳ Waiting for authorization...\n")
    
    time.sleep(10)  # Wait 10 seconds
    
    if server.get_auth_code():
        print(f"✅ Authorization code received: {server.get_auth_code()}")
    else:
        print("⏱️ No authorization code received (timeout)")
    
    server.stop()
