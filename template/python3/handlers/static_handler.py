# begin template/python3/handlers/static_handler.py
import os
import shutil
import html
from pathlib import Path
from config import MIME_TYPES

class StaticFileHandler:
    def __init__(self, request_handler):
        self.handler = request_handler

    def serve_static_file(self, path):
        """Serve a static file"""
        file_path = os.path.join(self.handler.directory, path)

        if not os.path.isfile(file_path):
            template_path = os.path.join(self.handler.directory, 'template', path)
            if os.path.isfile(template_path):
                file_path = template_path

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                content_type = self.get_content_type(file_path)
                self.handler.send_response(200)
                self.handler.send_header('Content-type', content_type)
                self.handler.send_header('Cache-Control', 'public, max-age=3600')
                self.handler.end_headers()
                self.handler.wfile.write(content)
            except Exception as e:
                print(f"Error serving {file_path}: {e}")
                self.handler.send_error(500, f"Internal server error: {str(e)}")
        else:
            self.handler.send_error(404, f"File not found: {path}")

    def ensure_index_html(self):
        """Ensure index.html exists in the home directory"""
        home_index = os.path.join(self.handler.directory, 'index.html')
        if not os.path.exists(home_index):
            template_index = os.path.join(self.handler.directory, 'template', 'html', 'index.html')
            if os.path.exists(template_index):
                with open(template_index, 'r', encoding='utf-8') as src:
                    content = src.read()
                with open(home_index, 'w', encoding='utf-8') as dst:
                    dst.write(content)
                print(f"Created index.html in home directory")

    def get_content_type(self, file_path):
        """Get the content type for a file"""
        ext = os.path.splitext(file_path)[1][1:].lower()
        return MIME_TYPES.get(ext, 'application/octet-stream')

    def serve_text_file_as_html(self):
        """Serve a text file as HTML"""
        path = os.path.join(self.handler.directory, self.handler.path[1:])
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.handler.send_response(200)
            self.handler.send_header("Content-type", "text/html; charset=utf-8")
            self.handler.end_headers()

            escaped_content = html.escape(content)
            html_content = self.generate_html_content(os.path.basename(path), escaped_content)
            self.handler.wfile.write(html_content.encode('utf-8'))
        except IOError:
            self.handler.send_error(404, "File not found")

    @staticmethod
    def generate_html_content(title, content):
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

    @staticmethod
    def setup_static_files(cls, directory):
        """Setup static files by copying them from template to static directories"""
        if cls.static_files_initialized:
            return

        static_dirs = ['css', 'js']
        for dir_name in static_dirs:
            static_dir = Path(directory) / dir_name
            template_dir = Path(directory) / 'template' / dir_name

            static_dir.mkdir(parents=True, exist_ok=True)

            if template_dir.exists():
                for file in template_dir.glob('*.*'):
                    dest_file = static_dir / file.name
                    if not dest_file.exists():
                        shutil.copy2(file, dest_file)
                        print(f"Copied {file} to {dest_file}")

        cls.static_files_initialized = True
# end template/python3/handlers/static_handler.py