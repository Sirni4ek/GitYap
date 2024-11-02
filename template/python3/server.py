#!/usr/bin/env python3

# begin template/python3/server.py ; marker comment, please do not remove

import argparse
import os
from http_handler import CustomHTTPRequestHandler
from utils import is_port_in_use, find_available_port
import socketserver
import asyncio
import websockets
from typing import Set
import json

class ChatServer:
	def __init__(self, port: int, directory: str):
		self.port = port
		self.directory = directory
		self.http_server = None
		self.websocket_server = None
		self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()

	async def register(self, websocket: websockets.WebSocketServerProtocol):
		self.connected_clients.add(websocket)
		try:
			async for message in websocket:
				# Handle incoming WebSocket messages
				await self.broadcast_message(message)
		finally:
			self.connected_clients.remove(websocket)

	async def broadcast_message(self, message: str):
		if self.connected_clients:
			await asyncio.gather(
				*[client.send(message) for client in self.connected_clients]
			)

	async def start_websocket_server(self):
		async with websockets.serve(self.register, "localhost", self.port + 1):
			await asyncio.Future()  # run forever

	def run(self):
		# Start HTTP server in a separate thread
		import threading
		http_thread = threading.Thread(
			target=run_server,
			args=(self.port, self.directory)
		)
		http_thread.daemon = True
		http_thread.start()

		# Start WebSocket server in the main thread
		asyncio.run(self.start_websocket_server())

def run_server(port: int, directory: str) -> socketserver.TCPServer:
	"""Run the HTTP server"""
	os.chdir(directory)
	CustomHTTPRequestHandler.setup_static_files(directory)

	try:
		httpd = socketserver.TCPServer(("", port), CustomHTTPRequestHandler)
		print(f"Serving HTTP on 0.0.0.0 port {port} (http://0.0.0.0:{port}/) ...")

		# Start serving in a separate thread
		import threading
		server_thread = threading.Thread(target=httpd.serve_forever)
		server_thread.daemon = True
		server_thread.start()

		return httpd
	except Exception as e:
		print(f"Error starting server: {e}")
		return None

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Run chat server with WebSocket support.")
	parser.add_argument('-p', '--port', type=int, default=8000, help='Port to serve on (default: 8000)')
	parser.add_argument('-d', '--directory', type=str, default=os.getcwd(), help='Directory to serve')

	args = parser.parse_args()

	if is_port_in_use(args.port):
		args.port = find_available_port(args.port + 1)
		print(f"Using port {args.port}...")

	server = ChatServer(args.port, args.directory)
	server.run()

# end server.py ; marker comment, please do not remove