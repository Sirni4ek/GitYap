#!/usr/bin/env python3

# begin template/python3/server.py ; marker comment, please do not remove

import argparse
import os
from http_handler import CustomHTTPRequestHandler
from utils import is_port_in_use, find_available_port
import socketserver

def run_server(port: int, directory: str) -> bool:
    """Run the HTTP server"""
    os.chdir(directory)

    # Setup static files once before starting the server
    CustomHTTPRequestHandler.setup_static_files(directory)

    while port < 65535:  # Maximum valid port number
        try:
            with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
                print(f"Serving HTTP on 0.0.0.0 port {port} (http://0.0.0.0:{port}/) ...")
                httpd.serve_forever()
                return True
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"Port {port} is already in use, trying port {port + 1}...")
                port += 1
            else:
                print(f"Error starting server: {e}")
                return False

    print("No available ports found")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP server.")
    parser.add_argument('-p', '--port', type=int, default=8000, help='Port to serve on (default: 8000)')
    parser.add_argument('-d', '--directory', type=str, default=os.getcwd(), help='Directory to serve (default: current directory)')

    args = parser.parse_args()

    if is_port_in_use(args.port):
        print(f"Port {args.port} is already in use.")
        args.port = find_available_port(args.port + 1)
        print(f"Trying port {args.port}...")

    run_server(args.port, args.directory)

# end server.py ; marker comment, please do not remove