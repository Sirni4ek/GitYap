# begin template/python3/file_operations.py ; marker comment, please do not remove

import os
import shutil
from pathlib import Path
from typing import List, Tuple
from config import SCRIPT_TYPES, INTERPRETER_MAP

def setup_static_files(directory):
	"""Setup static files by copying them from template to static directories"""
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

def find_scripts(directory: str, script_name: str) -> List[Tuple[str, str]]:
	"""Find all scripts matching the given name"""
	found_scripts = []
	for template_dir in os.listdir(os.path.join(directory, 'template')):
		for script_type in SCRIPT_TYPES:
			script_path = os.path.join(directory, 'template', template_dir, f"{script_name}.{script_type}")
			if os.path.exists(script_path):
				found_scripts.append((script_path, script_type))
	return found_scripts

# end file_operations.py ; marker comment, please do not remove