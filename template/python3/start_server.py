#!/usr/bin/env python3

# begin template/python3/start_server.py ; marker comment, please do not remove
# to run: python3 start_server.py

# start_server: v4

import argparse
import html
import http.server
import os
import random
import socket
import socketserver
import string
import subprocess
import time
import urllib.parse
import json
from datetime import datetime
from typing import List, Tuple
import shutil
from pathlib import Path

# Configuration constants
SCRIPT_TYPES = ['py', 'pl', 'rb', 'sh', 'js']
INTERPRETERS = ['python3', 'perl', 'ruby', 'bash', 'node']
INTERPRETER_MAP = dict(zip(SCRIPT_TYPES, INTERPRETERS))
MIME_TYPES = {
	'txt': 'text/plain',
	'html': 'text/html',
	'css': 'text/css',
	'js': 'application/javascript',
	'json': 'application/json',
	'png': 'image/png',
	'jpg': 'image/jpeg',
	'gif': 'image/gif',
}

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
	static_files_initialized = False  # Class variable to track initialization

	@classmethod
	def setup_static_files(cls, directory):
		"""Setup static files by copying them from template to static directories"""
		if cls.static_files_initialized:
			return

		# Create static directories if they don't exist
		static_dirs = ['css', 'js']
		for dir_name in static_dirs:
			static_dir = Path(directory) / dir_name
			template_dir = Path(directory) / 'template' / dir_name

			# Create directory if it doesn't exist
			static_dir.mkdir(parents=True, exist_ok=True)

			# Copy all files from template directory to static directory
			if template_dir.exists():
				for file in template_dir.glob('*.*'):
					dest_file = static_dir / file.name
					if not dest_file.exists():  # Only copy if file doesn't exist
						shutil.copy2(file, dest_file)
						print(f"Copied {file} to {dest_file}")

		cls.static_files_initialized = True

	def __init__(self, *args, **kwargs):
		self.directory = os.getcwd()  # Set default directory
		super().__init__(*args, directory=self.directory)

	def do_GET(self):
		"""Handle GET requests"""
		# Add handling for CSS files
		if self.path.startswith('/css/'):
			self.serve_static_file(self.path[1:])  # Remove leading slash
		elif self.path.startswith('/js/'):
			self.serve_static_file(self.path[1:])
		elif self.path in ['/', '/index.html']:
			self.ensure_index_html()
			self.serve_static_file('index.html')
		elif self.path == '/log.html':
			self.generate_and_serve_report()
		elif self.path == '/chat.html':
			self.generate_and_serve_chat()
		elif self.path == '/api/github_update':
			self.trigger_github_update()
		elif self.path.endswith('.txt'):
			self.serve_text_file_as_html()
		else:
			self.serve_static_file(self.path[1:])

	def do_POST(self):
		"""Handle POST requests"""
		if self.path == '/post':  # Changed from '/chat.html'
			self.handle_chat_post()
		else:
			self.send_error(405, "Method Not Allowed")

	def trigger_github_update(self):
		"""Trigger GitHub update and run the corresponding script"""
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write(b"Update triggered successfully")
		self.run_script('github_update')

	def save_message(self, author: str, message: str):
		"""Save a chat message to a file"""
		timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		title = self.generate_title(message)
		filename = f"{timestamp}_{title}.txt"

		message_dir = os.path.join(self.directory, 'message')
		os.makedirs(message_dir, exist_ok=True)

		filepath = os.path.join(message_dir, filename)
		with open(filepath, 'w', encoding='utf-8') as f:
			f.write(f"{message}\n\nAuthor: {author}")

	def generate_title(self, message: str) -> str:
		"""Generate a title for the message file"""
		if not message:
			return ''.join(random.choices(string.ascii_lowercase, k=10))

		words = message.split()[:5]
		title = '_'.join(words)
		safe_title = ''.join(c for c in title if c.isalnum() or c in ['_', '-'])
		return safe_title

	def generate_and_serve_report(self):
		"""Generate and serve the log report"""
		self.run_script_if_needed('log.html', 'log.html')
		self.serve_static_file('log.html')

	def generate_and_serve_chat(self):
		"""Generate and serve the chat page"""
		self.run_script_if_needed('chat.html', 'chat.html')
		self.serve_static_file('chat.html')

	def handle_chat_post(self):
		"""Handle POST request for chat messages"""
		try:
			content_length = int(self.headers.get('Content-Length', 0))
			if content_length > 1024 * 1024:  # 1MB limit
				self.send_error(413, "Request entity too large")
				return

			post_data = self.rfile.read(content_length).decode('utf-8')
			data = json.loads(post_data)

			# Sanitize and validate input
			author = html.escape(data.get('author', '').strip())[:50]  # Limit author length
			content = html.escape(data.get('content', '').strip())[:5000]  # Limit content length
			tags = [html.escape(tag.strip())[:30] for tag in data.get('tags', [])][:10]  # Limit tags

			if not author or not content:
				self.send_error(400, "Missing required fields")
				return

			# Create message directory if it doesn't exist
			message_dir = os.path.join(self.directory, 'message')
			os.makedirs(message_dir, exist_ok=True)

			# Generate timestamp and filename
			timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
			filename = f"{timestamp}.txt"
			filepath = os.path.join(message_dir, filename)

			# Write message to file
			with open(filepath, 'w', encoding='utf-8') as f:
				f.write(f"Author: {author}\n\n")
				f.write(content)
				if tags:
					f.write(f"\n\n{' '.join(tags)}")

			# Regenerate chat.html
			self.run_script('chat.html')

			# Send success response
			self.send_response(200)
			self.send_header('Content-type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps({'status': 'success'}).encode())

		except json.JSONDecodeError:
			self.send_error(400, "Bad Request: Invalid JSON")
		except Exception as e:
			self.send_error(500, str(e))

	def run_script_if_needed(self, output_filename: str, script_name: str):
		"""Run a script if the output file doesn't exist or is outdated"""
		output_filepath = os.path.join(self.directory, output_filename)
		if not os.path.exists(output_filepath) or \
		   time.time() - os.path.getmtime(output_filepath) > 60:
			print(f"Generating {output_filename}...")
			self.run_script(script_name)

	def run_script(self, script_name: str, *args):
		"""Run a script with the appropriate interpreter"""
		found_scripts = self.find_scripts(script_name)

		if not found_scripts:
			print(f"No scripts found for {script_name}")
			return

		for script_path, script_type in found_scripts:
			interpreter = INTERPRETER_MAP.get(script_type)
			if interpreter:
				subprocess.run([interpreter, script_path, *args], cwd=self.directory)

	def find_scripts(self, script_name: str) -> List[Tuple[str, str]]:
		"""Find all scripts matching the given name"""
		found_scripts = []
		for template_dir in os.listdir(os.path.join(self.directory, 'template')):
			for script_type in SCRIPT_TYPES:
				script_path = os.path.join(self.directory, 'template', template_dir, f"{script_name}.{script_type}")
				if os.path.exists(script_path):
					found_scripts.append((script_path, script_type))
		return found_scripts

	def serve_text_file_as_html(self):
		"""Serve a text file as HTML"""
		path = os.path.join(self.directory, self.path[1:])
		try:
			with open(path, 'r', encoding='utf-8') as f:
				content = f.read()

			self.send_response(200)
			self.send_header("Content-type", "text/html; charset=utf-8")
			self.end_headers()

			escaped_content = html.escape(content)
			html_content = self.generate_html_content(os.path.basename(path), escaped_content)
			self.wfile.write(html_content.encode('utf-8'))
		except IOError:
			self.send_error(404, "File not found")

	def ensure_index_html(self):
		"""Ensure index.html exists in the home directory"""
		home_index = os.path.join(self.directory, 'index.html')
		if not os.path.exists(home_index):
			template_index = os.path.join(self.directory, 'template', 'html', 'index.html')
			if os.path.exists(template_index):
				with open(template_index, 'r', encoding='utf-8') as src:
					content = src.read()
				with open(home_index, 'w', encoding='utf-8') as dst:
					dst.write(content)
				print(f"Created index.html in home directory")

	def generate_html_content(self, title: str, content: str) -> str:
		"""Generate HTML content for displaying text files"""
		return f"""
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1.0">
			<title>{title}</title>
			<style>
				body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
				pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }}
			</style>
		</head>
		<body>
			<h1>{title}</h1>
			<pre>{content}</pre>
		</body>
		</html>
		"""

	def serve_static_file(self, path: str):
		"""Serve a static file"""
		file_path = os.path.join(self.directory, path)

		# If file doesn't exist in root directory, check template directory
		if not os.path.isfile(file_path):
			template_path = os.path.join(self.directory, 'template', path)
			if os.path.isfile(template_path):
				file_path = template_path

		if os.path.isfile(file_path):
			try:
				with open(file_path, 'rb') as f:
					content = f.read()
				content_type = self.get_content_type(file_path)
				self.send_response(200)
				self.send_header('Content-type', content_type)
				self.send_header('Cache-Control', 'public, max-age=3600')  # Cache for 1 hour
				self.end_headers()
				self.wfile.write(content)
			except Exception as e:
				print(f"Error serving {file_path}: {e}")
				self.send_error(500, f"Internal server error: {str(e)}")
		else:
			self.send_error(404, f"File not found: {path}")

	def get_content_type(self, file_path: str) -> str:
		"""Get the content type for a file"""
		ext = os.path.splitext(file_path)[1][1:].lower()
		return MIME_TYPES.get(ext, 'application/octet-stream')

def is_port_in_use(port: int) -> bool:
	"""Check if a port is already in use"""
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port: int) -> int:
	"""Find an available port starting from the given port"""
	port = start_port
	while is_port_in_use(port):
		port += 1
	return port

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

# end start_server.py ; marker comment, please do not remove`