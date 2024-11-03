# begin template/python3/handlers/chat_handler.py ; marker comment, please include this, including this comment
import os
import re
from datetime import datetime
from utils import page_cache, git_cache
import json

class ChatHandler:
	def __init__(self, request_handler):
		self.handler = request_handler

	def handle_chat_get_request(self, path):
		"""Handle GET requests for chat pages"""
		parts = path.split('/')
		if len(parts) != 3:
			self.handler.send_error(404, "Invalid channel URL")
			return

		channel = parts[2]
		if channel.endswith('.html'):
			channel = channel[:-5]  # Remove .html extension

		print(f"Processing chat request for channel: {channel}")

		if not self.is_valid_channel_name(channel):
			self.handler.send_error(400, "Invalid channel name")
			return

		# Create chat directory if it doesn't exist
		chat_dir = os.path.join(self.handler.directory, 'chat')
		os.makedirs(chat_dir, exist_ok=True)

		# Create message directory for channel if it doesn't exist
		message_dir = os.path.join(self.handler.directory, 'message', channel)
		os.makedirs(message_dir, exist_ok=True)

		self.generate_and_serve_chat(channel)

	def generate_and_serve_chat(self, channel='general'):
		"""Generate and serve the chat page with caching"""
		print(f"Generating chat page for channel: {channel}")

		# New file path structure - use absolute path from the start
		chat_dir = os.path.join(self.handler.directory, 'chat')
		os.makedirs(chat_dir, exist_ok=True)  # Ensure chat directory exists
		output_file = os.path.join(self.handler.directory, 'chat', f'{channel}.html')

		# Also check for old-style filename
		old_output_file = os.path.join(self.handler.directory, 'chat', f'{channel}_{channel}.html')
		if os.path.exists(old_output_file):
			try:
				os.remove(old_output_file)
				print(f"Removed old-style file: {old_output_file}")
			except Exception as e:
				print(f"Error removing old file {old_output_file}: {e}")

		cache_key = f'chat_{channel}'
		cached_content = page_cache.get(cache_key)

		#if cached_content: #todo fix this to not use cache if a new comment was just posted
		#	print(f"Serving cached content for channel: {channel}")
		#	self.handler.send_response(200)
		#	self.handler.send_header('Content-type', 'text/html')
		#	self.handler.end_headers()
		#	self.handler.wfile.write(cached_content.encode('utf-8'))
		#	return

		self.schedule_git_pull(channel)

		# Force regenerate the file if it exists
		if os.path.exists(output_file):
			try:
				os.remove(output_file)
				print(f"Removed existing {output_file}")
			except Exception as e:
				print(f"Error removing {output_file}: {e}")

		print(f"Running chat.html.py script for channel: {channel}")
		try:
			# Use absolute path for output file
			self.handler.script_handler.run_script(
				'chat.html.py',
				'--channel', channel,
				'--output_file', output_file
			)
		except Exception as e:
			print(f"Error running chat.html.py script: {e}")

		if os.path.exists(output_file):
			try:
				with open(output_file, 'rb') as f:
					content = f.read()
				page_cache.set(cache_key, content.decode('utf-8'))
				self.handler.send_response(200)
				self.handler.send_header('Content-type', 'text/html')
				self.handler.end_headers()
				self.handler.wfile.write(content)
				print(f"Successfully served chat page for channel: {channel}")
			except Exception as e:
				print(f"Error reading {output_file}: {e}")
				self.handler.send_error(500, f"Error reading chat page: {str(e)}")
		else:
			print(f"Failed to generate {output_file}")
			self.handler.send_error(500, "Failed to generate chat page")

	def schedule_git_pull(self, channel):
		"""Schedule git pull in background"""
		import threading
		def pull_async():
			channel_repo_path = os.path.join(self.handler.directory, 'message', channel)
			if os.path.exists(channel_repo_path):
				from commit_files import pull_changes
				if pull_changes(channel_repo_path):
					page_cache.invalidate(f'chat/{channel}') #todo is this right?
					git_cache.invalidate(channel)

		thread = threading.Thread(target=pull_async)
		thread.daemon = True
		thread.start()

	@staticmethod
	def is_valid_channel_name(channel):
		"""Validate channel name to prevent directory traversal and invalid names"""
		if channel == 'chat':
			return True
		return bool(re.match(r'^[a-zA-Z0-9_-]+$', channel))

	def generate_and_serve_report(self):
		"""Generate and serve the log report"""
		self.handler.script_handler.run_script_if_needed('log.html', 'log.html')
		self.handler.static_handler.serve_static_file('log.html')

	def handle_chat_post(self):
		"""Handle POST request for chat messages"""
		try:
			print("\n=== Starting chat post handling ===")

			# Get and decode request data
			content_length = int(self.handler.headers.get('Content-Length', 0))
			print(f"Content Length: {content_length}")
			post_data = self.handler.rfile.read(content_length).decode('utf-8')
			print(f"Raw POST data: {post_data}")

			# Parse JSON data
			try:
				data = json.loads(post_data)
				print(f"Parsed data: {json.dumps(data, indent=2)}")
			except json.JSONDecodeError as e:
				print(f"JSON decode error: {str(e)}")
				self._send_json_response({
					'error': 'Invalid JSON format',
					'debug_info': {
						'error_message': str(e),
						'error_position': e.pos,
						'raw_data': post_data
					}
				}, 400)
				return

			# Extract fields
			author = data.get('author', 'Guest')
			content = data.get('content', '')
			tags = data.get('tags', [])
			channel = data.get('channel', 'general')

			print(f"Extracted fields:")
			print(f"- Author: {author}")
			print(f"- Content: {content}")
			print(f"- Tags: {tags}")
			print(f"- Channel: {channel}")

			if not content:
				print("Error: Missing content")
				self._send_json_response({
					'error': 'Missing content',
					'debug_info': {'received_data': data}
				}, 400)
				return

			if not self.is_valid_channel_name(channel):
				print(f"Error: Invalid channel name: {channel}")
				self._send_json_response({
					'error': 'Invalid channel name',
					'debug_info': {'channel': channel}
				}, 400)
				return

			# Create message directory
			message_dir = os.path.join(self.handler.directory, 'message', channel)
			print(f"Message directory path: {message_dir}")

			try:
				os.makedirs(message_dir, exist_ok=True)
				print(f"Created/verified directory at: {message_dir}")
			except OSError as e:
				print(f"Error creating directory: {str(e)}")
				self._send_json_response({
					'error': 'Failed to create message directory',
					'debug_info': {'error': str(e)}
				}, 500)
				return

			# Generate timestamp and filename
			timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
			filename = f"{timestamp}.txt"
			filepath = os.path.join(message_dir, filename)
			print(f"Will save message to: {filepath}")

			# Write message to file
			try:
				with open(filepath, 'w', encoding='utf-8') as f:
					f.write(f"Author: {author}\n")
					f.write(f"Channel: {channel}\n")
					#f.write(f"Timestamp: {timestamp}\n\n") #todo
					f.write(content)
					if tags:
						f.write(f"\n\nTags: {' '.join(tags)}")
			except IOError as e:
				print(f"Error writing file: {str(e)}")
				self._send_json_response({
					'error': 'Failed to write message',
					'debug_info': {'error': str(e)}
				}, 500)
				return

			# Regenerate chat.html
			print("Regenerating chat.html...")
			try:
				self.generate_and_serve_chat(channel)
				print("Successfully regenerated chat.html")
			except Exception as e:
				print(f"Error regenerating chat.html: {str(e)}")

			# Invalidate cache
			page_cache.invalidate(f'chat/{channel}')
			git_cache.invalidate(channel)

			print("=== Chat post handling complete ===\n")
			self._send_json_response({
				'status': 'success',
				'timestamp': timestamp,
				'debug_info': {
					'filepath': filepath,
					'channel': channel,
					'message_length': len(content)
				}
			})

		except Exception as e:
			import traceback
			trace = traceback.format_exc()
			print(f"Unexpected error: {str(e)}")
			print(f"Traceback:\n{trace}")
			self._send_json_response({
				'error': str(e),
				'debug_info': {
					'traceback': trace,
					'error_type': type(e).__name__
				}
			}, 500)

	def _send_json_response(self, data, status=200):
		"""Helper method to send JSON responses"""
		response = json.dumps(data)
		response_bytes = response.encode('utf-8')

		self.handler.send_response(status)
		self.handler.send_header('Content-Type', 'application/json')
		self.handler.send_header('Content-Length', len(response_bytes))
		self.handler.send_header('Cache-Control', 'no-cache')
		self.handler.end_headers()
		self.handler.wfile.write(response_bytes)

# end chat_handler.py ; marker comment, please include this, including this comment