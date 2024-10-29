# begin template/python3/http/request_handler.py
import json
import urllib.parse
from datetime import datetime

class RequestHandler:
	def __init__(self, request_handler):
		self.handler = request_handler

	def handle_post_request(self, path):
		"""Route POST requests to appropriate handlers"""
		parsed_path = urllib.parse.urlparse(path)
		path = parsed_path.path

		if path == '/sync':
			self.handle_sync_request()
		elif path in ['/post', '/chat.html']:
			self.handle_chat_post()
		else:
			self.handler.send_error(405, "Method Not Allowed")

	def handle_sync_request(self):
		"""Handle manual sync request"""
		try:
			content_length = int(self.handler.headers.get('Content-Length', 0))
			post_data = self.handler.rfile.read(content_length).decode('utf-8')
			data = json.loads(post_data)

			channel = data.get('channel', 'general')
			if not self.handler.chat_handler.is_valid_channel_name(channel):
				self.send_json_response({'error': 'Invalid channel name'}, status=400)
				return

			channel_repo_path = os.path.join(self.handler.directory, 'message', channel)
			if os.path.exists(channel_repo_path):
				from commit_files import pull_changes
				if pull_changes(channel_repo_path):
					# Invalidate cache after successful sync
					page_cache.invalidate(f'chat_{channel}')
					git_cache.invalidate(channel)
					self.send_json_response({'status': 'success'})
				else:
					self.send_json_response({'error': 'Sync failed'}, status=500)
			else:
				self.send_json_response({'error': 'Channel not found'}, status=404)
		except json.JSONDecodeError as e:
			self.send_json_response({'error': f'Invalid JSON: {str(e)}'}, status=400)
		except Exception as e:
			self.send_json_response({'error': str(e)}, status=500)

	def send_json_response(self, data, status=200):
		"""Send a JSON response with the specified status code"""
		response = json.dumps(data)
		self.handler.send_response(status)
		self.handler.send_header('Content-Type', 'application/json')
		self.handler.send_header('Content-Length', len(response.encode('utf-8')))
		self.handler.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
		self.handler.send_header('Pragma', 'no-cache')
		self.handler.send_header('Expires', '0')
		self.handler.end_headers()
		self.handler.wfile.write(response.encode('utf-8'))
# end template/python3/http/request_handler.py