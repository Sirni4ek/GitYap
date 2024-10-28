# begin template/python3/file_operations.py ; marker comment, please do not remove

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple
from config import SCRIPT_TYPES, INTERPRETER_MAP, DEFAULT_CHANNELS
from commit_files import init_git_repo, run_git_command

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

def initialize_channel(channel_dir: Path, channel_config: dict) -> bool:
	"""Initialize a single channel directory with git repository"""
	try:
		# Create channel directory if it doesn't exist
		channel_dir.mkdir(parents=True, exist_ok=True)

		# Initialize git repository
		if not init_git_repo(str(channel_dir)):
			return False

		# Create README.md with channel description
		readme_path = channel_dir / 'README.md'
		with open(readme_path, 'w') as f:
			f.write(f"# {channel_config['name']}\n\n{channel_config['description']}")

		# If remote repository URL is provided, set it up
		if channel_config.get('repo'):
			cmd = f"git -C {channel_dir} remote add origin {channel_config['repo']}"
			output, error = run_git_command(cmd)
			if error:
				print(f"Error setting up remote for {channel_config['name']}: {error}")
				return False

		# Commit README
		run_git_command(f"git -C {channel_dir} add README.md")
		run_git_command(f"git -C {channel_dir} commit -m 'Initialize channel {channel_config['name']}'")

		return True
	except Exception as e:
		print(f"Error initializing channel {channel_config['name']}: {str(e)}")
		return False

def setup_default_channels(base_directory: str) -> None:
	"""Setup default channels in the messages directory"""
	messages_dir = Path(base_directory) / 'messages'
	messages_dir.mkdir(parents=True, exist_ok=True)

	for channel in DEFAULT_CHANNELS:
		channel_dir = messages_dir / channel['name']
		if not channel_dir.exists():
			print(f"Initializing channel: {channel['name']}")
			if initialize_channel(channel_dir, channel):
				print(f"Successfully initialized channel: {channel['name']}")
			else:
				print(f"Failed to initialize channel: {channel['name']}")

# end file_operations.py ; marker comment, please do not remove