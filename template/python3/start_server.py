#!/usr/bin/env python3

# begin template/python3/start_server.py ; marker comment, please do not remove
# to run: python3 start_server.py

# start_server: v4

import argparse
import os
import webbrowser
from server import run_server
from utils import is_port_in_use, find_available_port
import time

def main():
	parser = argparse.ArgumentParser(description="Run a simple HTTP server.")
	parser.add_argument('-p', '--port', type=int, default=8000,
					   help='Port to serve on (default: 8000)')
	parser.add_argument('-d', '--directory', type=str, default=os.getcwd(),
					   help='Directory to serve (default: current directory)')

	args = parser.parse_args()

	# Find an available port
	port = args.port
	while is_port_in_use(port):
		print(f"Port {port} is already in use.")
		port = find_available_port(port + 1)
		print(f"Trying port {port}...")

	# Start the server
	httpd = run_server(port, args.directory)

	if httpd is not None:
		# Give the server a moment to start
		time.sleep(0.5)

		# Open the browser with the correct port
		url = f"http://localhost:{port}"
		webbrowser.open(url)
		print(f"Server is running on {url}")

		try:
			# Keep the main thread running
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			print("\nShutting down server...")
			httpd.shutdown()
			httpd.server_close()
	else:
		print("Failed to start server")

if __name__ == "__main__":
	main()

# end start_server.py ; marker comment, please do not remove