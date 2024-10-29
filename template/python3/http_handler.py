# begin template/python3/http_handler.py
import os
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

from handlers.request_handler import RequestHandler
from handlers.static_handler import StaticFileHandler
from handlers.chat_handler import ChatHandler
from handlers.script_handler import ScriptHandler

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
	static_files_initialized = False
	base_directory = None  # Class variable to store the base directory

	def __init__(self, *args, **kwargs):
		if CustomHTTPRequestHandler.base_directory is None:
			CustomHTTPRequestHandler.base_directory = os.getcwd()
		self.directory = CustomHTTPRequestHandler.base_directory

		# Initialize handlers before calling parent's __init__
		self.request_handler = RequestHandler(self)
		self.static_handler = StaticFileHandler(self)
		self.chat_handler = ChatHandler(self)
		self.script_handler = ScriptHandler(self)

		# Call parent's __init__ with the correct arguments
		SimpleHTTPRequestHandler.__init__(self, *args, directory=self.directory)

	@property
	def template_directory(self):
		"""Get the template directory path"""
		return os.path.join(self.directory, 'template', 'python3')

	def do_GET(self):
		"""Handle GET requests with improved channel validation"""
		if self.path.startswith(('/css/', '/js/')):
			self.static_handler.serve_static_file(self.path[1:])
		elif self.path in ['/', '/index.html']:
			self.static_handler.ensure_index_html()
			self.static_handler.serve_static_file('index.html')
		elif self.path == '/log.html':
			self.chat_handler.generate_and_serve_report()
		elif self.path.startswith('/chat/'):
			self.chat_handler.handle_chat_get_request(self.path)
		elif self.path == '/chat.html':
			self.chat_handler.generate_and_serve_chat('general')
		elif self.path.endswith('.txt'):
			self.static_handler.serve_text_file_as_html()
		else:
			self.send_error(404, "File not found")

	def do_POST(self):
		"""Handle POST requests"""
		self.request_handler.handle_post_request(self.path)

	@classmethod
	def setup_static_files(cls, directory):
		"""Setup static files by copying them from template to static directories"""
		cls.base_directory = directory
		StaticFileHandler.setup_static_files(cls, directory)
# end http_handler.py