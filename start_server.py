#!/usr/bin/env python3
"""
Start the LPC Character Generator local development server.
Serves the lpc_generator directory on localhost:8000.
"""

import http.server
import socketserver
import os
import sys

PORT = 8000
DIRECTORY = "lpc_generator"

def main():
    # Change to the lpc_generator directory
    if not os.path.exists(DIRECTORY):
        print(f"Error: '{DIRECTORY}' directory not found.")
        print("Please run this script from the root of the lpc project.")
        sys.exit(1)

    os.chdir(DIRECTORY)

    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        print(f"Serving directory: {os.getcwd()}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()
