#!/usr/bin/env python3

# begin template/python3/start_server.py ; marker comment, please do not remove
# to run: python3 start_server.py

# start_server: v4

import argparse
import os
from server import run_server
from utils import is_port_in_use, find_available_port

def main():
	parser = argparse.ArgumentParser(description="Run a simple HTTP server.")
	parser.add_argument('-p', '--port', type=int, default=8000,
					   help='Port to serve on (default: 8000)')
	parser.add_argument('-d', '--directory', type=str, default=os.getcwd(),
					   help='Directory to serve (default: current directory)')

	args = parser.parse_args()

	if is_port_in_use(args.port):
		print(f"Port {args.port} is already in use.")
		args.port = find_available_port(args.port + 1)
		print(f"Trying port {args.port}...")

	run_server(args.port, args.directory)

if __name__ == "__main__":
	main()

# end start_server.py ; marker comment, please do not remove