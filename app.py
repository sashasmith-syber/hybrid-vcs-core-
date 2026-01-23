#!/usr/bin/env python3
"""
Simple app.py to start the Hybrid VCS web server for the Comet Browser extension.
"""

import logging
import time
import sys

from hybrid_vcs import create_server

def main():
    """Start the Hybrid VCS web server."""
    print("🚀 Starting Comet Browser VCS Web Server")
    print("=" * 50)
    print("Host: localhost")
    print("Port: 8081")
    print("Press Ctrl+C to stop")
    print()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    )

    try:
        # Create and start the server
        server = create_server(host='localhost', port=8081)
        server.start()

        print("✅ Server started successfully!")
        print("🌐 API endpoints available at: http://localhost:8081")
        print()
        print("Available endpoints:")
        print("  GET  /health                    - Server health check")
        print("  GET  /api/history              - Get content history")
        print("  POST /api/save-page            - Save webpage content")
        print("  POST /api/save-selection       - Save text selection")
        print("  POST /api/save-link            - Save link data")
        print("  GET  /api/versions/{commit}    - Get version content")
        print()
        print("🎯 Ready for Comet Browser extension connections!")

        # Keep running until interrupted
        try:
            while server.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Shutdown requested...")

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1

    finally:
        if 'server' in locals():
            print("🛑 Stopping server...")
            server.stop()
            print("✅ Server stopped")

    return 0

if __name__ == "__main__":
    sys.exit(main())