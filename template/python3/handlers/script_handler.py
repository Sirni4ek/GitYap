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
		found_scripts = self.find_scripts(script_name)

		if not found_scripts:
			print(f"No scripts found for {script_name}")
			return

		for script_path, script_type in found_scripts:
			interpreter = INTERPRETER_MAP.get(script_type)
			if interpreter:
				cmd = [interpreter, script_path]
				if args:  # Add any additional arguments
					cmd.extend(str(arg) for arg in args)
				print(f"Running command: {' '.join(cmd)}")  # Debug logging
				try:
					subprocess.run(cmd, cwd=self.handler.directory, check=True)
				except subprocess.CalledProcessError as e:
					print(f"Error running script: {e}")
				except Exception as e:
					print(f"Unexpected error running script: {e}")

	def find_scripts(self, script_name: str) -> List[Tuple[str, str]]:
		"""Find all scripts matching the given name"""
		found_scripts = []
		template_dir = self.handler.template_directory

		if os.path.exists(template_dir):
			for script_type in SCRIPT_TYPES:
				# Handle both with and without extension
				base_name = script_name
				if '.' in script_name:
					base_name = script_name.split('.')[0]

				script_path = os.path.join(template_dir, f"{base_name}.{script_type}")
				if os.path.exists(script_path):
					found_scripts.append((script_path, script_type))

		if not found_scripts:
			print(f"No scripts found in {template_dir} for {script_name}")
			print(f"Available files: {os.listdir(template_dir)}")

		return found_scripts

	def run_script_if_needed(self, output_filename: str, script_name: str, *args):
		"""Run a script if the output file doesn't exist or is outdated"""
		output_filepath = os.path.join(self.handler.directory, output_filename)
		if not os.path.exists(output_filepath) or \
		   time.time() - os.path.getmtime(output_filepath) > 60:
			print(f"Generating {output_filename}...")
			self.run_script(script_name, *args)
# end template/python3/handlers/script_handler.py