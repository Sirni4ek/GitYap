# begin template/python3/handlers/script_handler.py
import os
import subprocess
import time
from typing import List, Tuple
from config import INTERPRETER_MAP, SCRIPT_TYPES

class ScriptHandler:
    def __init__(self, request_handler):
        self.handler = request_handler

    def run_script(self, script_name: str, *args):
        """Run a script with the appropriate interpreter and arguments"""
        script_path = os.path.join(self.handler.template_directory, script_name)

        if not os.path.exists(script_path):
            print(f"Script not found: {script_path}")
            return

        # Determine script type from extension
        ext = os.path.splitext(script_name)[1][1:]  # Remove the dot
        interpreter = INTERPRETER_MAP.get(ext)

        if not interpreter:
            print(f"No interpreter found for extension: {ext}")
            return

        cmd = [interpreter, script_path] + list(args)
        print(f"Running command: {' '.join(cmd)}")  # Debug logging
        print(f"Working directory: {self.handler.directory}")  # Debug logging

        try:
            result = subprocess.run(
                cmd,
                cwd=self.handler.directory,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Script output: {result.stdout}")
            if result.stderr:
                print(f"Script errors: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Error running script: {e}")
            print(f"Script output: {e.output}")
            print(f"Script errors: {e.stderr}")
        except Exception as e:
            print(f"Unexpected error running script: {e}")

    def run_script_if_needed(self, output_filename: str, script_name: str, *args):
        """Run a script if the output file doesn't exist or is outdated"""
        output_filepath = os.path.join(self.handler.directory, output_filename)
        if not os.path.exists(output_filepath) or \
           time.time() - os.path.getmtime(output_filepath) > 60:
            print(f"Generating {output_filename}...")
            self.run_script(script_name, *args)
# end template/python3/handlers/script_handler.py