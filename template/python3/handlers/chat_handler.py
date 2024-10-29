# begin template/python3/handlers/chat_handler.py
    def generate_and_serve_chat(self, channel='general'):
        """Generate and serve the chat page with caching"""
        print(f"Generating chat page for channel: {channel}")

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

        # New file path structure
        chat_dir = os.path.join(self.handler.directory, 'chat')
        os.makedirs(chat_dir, exist_ok=True)  # Ensure chat directory exists
        output_file = os.path.join(chat_dir, f'{channel}.html')

        # Force regenerate the file if it exists
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                print(f"Removed existing {output_file}")
            except Exception as e:
                print(f"Error removing {output_file}: {e}")

        print(f"Running chat.html.py script for channel: {channel}")
        try:
            self.handler.script_handler.run_script('chat.html.py', '--channel', channel, '--output', output_file)
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
# end template/python3/handlers/chat_handler.py