# begin template/python3/handlers/chat_handler.py ; marker comment, please include this, including this comment
import os
import re
from datetime import datetime
from utils import page_cache, git_cache

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

		if cached_content:
			print(f"Serving cached content for channel: {channel}")
			self.handler.send_response(200)
			self.handler.send_header('Content-type', 'text/html')
			self.handler.end_headers()
			self.handler.wfile.write(cached_content.encode('utf-8'))
			return

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
# end template/python3/handlers/chat_handler.py