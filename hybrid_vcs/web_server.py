"""
Web server for Hybrid VCS browser extension API.
Provides REST endpoints for web content versioning.
"""

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional
import threading
import time

from .core import HybridVCS

logger = logging.getLogger(__name__)


class VCSExtensionHandler(BaseHTTPRequestHandler):
    """HTTP request handler for VCS extension API."""

    def __init__(self, vcs_instance: HybridVCS, *args, **kwargs):
        self.vcs = vcs_instance
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        try:
            path = urlparse(self.path).path

            if path == '/health':
                self._send_json_response(200, {'status': 'healthy', 'connected': True})
            elif path == '/api/history':
                self._handle_get_history()
            elif path.startswith('/api/versions/'):
                commit_hash = path.split('/api/versions/')[1]
                self._handle_get_version(commit_hash)
            else:
                self._send_json_response(404, {'error': 'Endpoint not found'})

        except Exception as e:
            logger.error(f"GET request error: {e}")
            self._send_json_response(500, {'error': str(e)})

    def do_POST(self):
        """Handle POST requests."""
        try:
            path = urlparse(self.path).path
            content_length = int(self.headers.get('Content-Length', 0))

            if content_length == 0:
                self._send_json_response(400, {'error': 'No data provided'})
                return

            # Read request body
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            if path == '/api/save-page':
                self._handle_save_page(data)
            elif path == '/api/save-selection':
                self._handle_save_selection(data)
            elif path == '/api/save-link':
                self._handle_save_link(data)
            else:
                self._send_json_response(404, {'error': 'Endpoint not found'})

        except json.JSONDecodeError:
            self._send_json_response(400, {'error': 'Invalid JSON data'})
        except Exception as e:
            logger.error(f"POST request error: {e}")
            self._send_json_response(500, {'error': str(e)})

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def _handle_save_page(self, data: Dict[str, Any]):
        """Handle save webpage request."""
        try:
            commit_hash = self.vcs.save_webpage(data)
            self._send_json_response(200, {
                'success': True,
                'commit_hash': commit_hash,
                'message': 'Webpage saved successfully'
            })
        except Exception as e:
            logger.error(f"Save webpage error: {e}")
            self._send_json_response(500, {'error': f'Failed to save webpage: {str(e)}'})

    def _handle_save_selection(self, data: Dict[str, Any]):
        """Handle save text selection request."""
        try:
            commit_hash = self.vcs.save_text_selection(data)
            self._send_json_response(200, {
                'success': True,
                'commit_hash': commit_hash,
                'message': 'Text selection saved successfully'
            })
        except Exception as e:
            logger.error(f"Save selection error: {e}")
            self._send_json_response(500, {'error': f'Failed to save selection: {str(e)}'})

    def _handle_save_link(self, data: Dict[str, Any]):
        """Handle save link request."""
        try:
            commit_hash = self.vcs.save_link(data)
            self._send_json_response(200, {
                'success': True,
                'commit_hash': commit_hash,
                'message': 'Link saved successfully'
            })
        except Exception as e:
            logger.error(f"Save link error: {e}")
            self._send_json_response(500, {'error': f'Failed to save link: {str(e)}'})

    def _handle_get_history(self):
        """Handle get history request."""
        try:
            # Parse query parameters
            query = urlparse(self.path).query
            params = parse_qs(query)
            limit = int(params.get('limit', ['50'])[0])

            history = self.vcs.get_content_history(limit)
            self._send_json_response(200, {
                'success': True,
                'history': history
            })
        except Exception as e:
            logger.error(f"Get history error: {e}")
            self._send_json_response(500, {'error': f'Failed to get history: {str(e)}'})

    def _handle_get_version(self, commit_hash: str):
        """Handle get version content request."""
        try:
            content = self.vcs.get_version_content(commit_hash)
            if content:
                self._send_json_response(200, {
                    'success': True,
                    'content': content
                })
            else:
                self._send_json_response(404, {'error': 'Version not found'})
        except Exception as e:
            logger.error(f"Get version error: {e}")
            self._send_json_response(500, {'error': f'Failed to get version: {str(e)}'})

    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response with proper headers."""
        self.send_response(status_code)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))

    def _set_cors_headers(self):
        """Set CORS headers for browser requests."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"HTTP {format % args}")


class VCSWebServer:
    """Web server for Hybrid VCS browser extension."""

    def __init__(self, vcs_instance: HybridVCS, host: str = 'localhost', port: int = 8080):
        self.vcs = vcs_instance
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False

        # Create custom handler class with VCS instance
        def handler_class(*args, **kwargs):
            return VCSExtensionHandler(vcs_instance, *args, **kwargs)

        self.handler_class = handler_class

    def start(self):
        """Start the web server in a background thread."""
        if self.running:
            logger.warning("Web server is already running")
            return

        try:
            self.server = HTTPServer((self.host, self.port), self.handler_class)
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()
            self.running = True
            logger.info(f"VCS Web Server started on http://{self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            raise

    def stop(self):
        """Stop the web server."""
        if not self.running:
            return

        logger.info("Stopping VCS Web Server...")
        if self.server:
            self.server.shutdown()
            self.server.server_close()

        if self.thread:
            self.thread.join(timeout=5)

        self.running = False
        logger.info("VCS Web Server stopped")

    def _run_server(self):
        """Run the server (called in background thread)."""
        try:
            logger.info(f"VCS Web Server listening on http://{self.host}:{self.port}")
            self.server.serve_forever()
        except Exception as e:
            logger.error(f"Web server error: {e}")
        finally:
            self.running = False

    def is_running(self) -> bool:
        """Check if the server is running."""
        return self.running


def create_server(vcs_config: Optional[Dict[str, Any]] = None, host: str = 'localhost', port: int = 8080) -> VCSWebServer:
    """
    Create and configure a VCS web server.

    Args:
        vcs_config: Configuration for VCS instance
        host: Server host (default: localhost)
        port: Server port (default: 8080)

    Returns:
        Configured VCSWebServer instance
    """
    vcs = HybridVCS(vcs_config)
    server = VCSWebServer(vcs, host, port)
    return server


if __name__ == '__main__':
    # Simple CLI for testing
    import sys

    logging.basicConfig(level=logging.INFO)

    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080

    print(f"Starting VCS Web Server on {host}:{port}")
    print("Press Ctrl+C to stop")

    server = create_server(host=host, port=port)
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()