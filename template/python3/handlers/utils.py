# begin template/python3/http/utils.py
import os
import subprocess
from typing import List, Tuple
from config import INTERPRETER_MAP, SCRIPT_TYPES

def run_script(directory: str, script_name: str, *args):
	"""Run a script with the appropriate interpreter and arguments"""
	found_scripts = find_scripts(directory, script_name)

	if not found_scripts:
		print(f"No scripts found for {script_name}")
		return

	for script_path, script_type in found_scripts:
		interpreter = INTERPRETER_MAP.get(script_type)
		if interpreter:
			cmd = [interpreter, script_path]
			if args:
				cmd.extend(str(arg) for arg in args)
			subprocess.run(cmd, cwd=directory)

def find_scripts(directory: str, script_name: str) -> List[Tuple[str, str]]:
	"""Find all scripts matching the given name"""
	found_scripts = []
	template_dir = os.path.join(directory, 'template')
	if os.path.exists(template_dir):
		for subdir in os.listdir(template_dir):
			for script_type in SCRIPT_TYPES:
				script_path = os.path.join(template_dir, subdir, f"{script_name}.{script_type}")
				if os.path.exists(script_path):
					found_scripts.append((script_path, script_type))
	return found_scripts

def generate_html_content(title: str, content: str) -> str:
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
# end template/python3/http/utils.py