# begin template/python3/commit_files.py ; marker comment, please do not remove
# to run: python3 commit_files.py

# File: commit_files.py

import os
import re
import subprocess
import sys
from datetime import datetime
import json
import hashlib

def calculate_file_hash(file_path):
	sha256_hash = hashlib.sha256()
	with open(file_path, "rb") as f:
		for byte_block in iter(lambda: f.read(4096), b""):
			sha256_hash.update(byte_block)
	return sha256_hash.hexdigest()

def extract_metadata(content, file_path):
	metadata = {
		'author': '',
		'title': os.path.basename(file_path),
		'hashtags': [],
		'file_hash': calculate_file_hash(file_path)
	}

	# Extract author
	author_match = re.search(r'Author:\s*(.+)', content)
	if author_match:
		metadata['author'] = author_match.group(1)

	# Extract title (assuming it's the first line of the file)
	title_match = re.search(r'^(.+)', content)
	if title_match:
		metadata['title'] = title_match.group(1).strip()

	# Extract hashtags
	metadata['hashtags'] = re.findall(r'#\w+', content)

	return metadata

def store_metadata(file_path, metadata):
	metadata_dir = os.path.join(os.path.dirname(file_path), 'metadata')
	os.makedirs(metadata_dir, exist_ok=True)

	metadata_file = os.path.join(metadata_dir, f"{os.path.basename(file_path)}.json")

	with open(metadata_file, 'w', encoding='utf-8') as f:
		json.dump(metadata, f, indent=2)

	return metadata_file

def run_git_command(command):
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output, error = process.communicate()
	return output.decode('utf-8').strip(), error.decode('utf-8').strip()

def has_remote():
	"""Check if the repository has a remote configured"""
	output, error = run_git_command("git remote")
	return bool(output.strip())

def can_push():
	"""Check if we can push to the remote"""
	if not has_remote():
		return False

	# Try to get the remote URL
	output, error = run_git_command("git remote get-url origin")
	if error or not output:
		return False

	# Check if we have credentials configured
	output, error = run_git_command("git config --get remote.origin.url")
	return bool(output.strip())

def push_changes():
	"""Push changes to remote if possible"""
	if not can_push():
		print("No remote configured or push access not available")
		return False

	output, error = run_git_command("git push origin HEAD")
	if error and "rejected" in error.lower():
		print(f"Push failed: {error}")
		return False

	print("Successfully pushed changes to remote repository")
	return True

def init_git_repo(repo_path):
	"""Initialize a git repository if it doesn't exist"""
	git_dir = os.path.join(repo_path, '.git')
	if not os.path.exists(git_dir):
		output, error = run_git_command(f"git init {repo_path}")
		if error:
			print(f"Error initializing git repo: {error}")
			return False
		print(f"Initialized git repository in {repo_path}")

		# Set default git config for the repo
		run_git_command(f"git -C {repo_path} config user.name 'Chat Bot'")
		run_git_command(f"git -C {repo_path} config user.email 'chat@bot.local'")
		return True
	return True

def commit_text_files(repo_path=".", initialize=True):
	"""Modified to handle repository initialization"""
	if initialize and not init_git_repo(repo_path):
		print("Failed to initialize git repository")
		return False

	curr_dir = os.getcwd()
	os.chdir(repo_path)

	try:
		# Check if there are any changes
		status_output, _ = run_git_command("git status --porcelain")
		if not status_output:
			print("No changes to commit.")
			return True

		# Get all modified and untracked files
		changed_files, _ = run_git_command("git diff --name-only")
		untracked_files, _ = run_git_command("git ls-files --others --exclude-standard")

		all_files = changed_files.split('\n') + untracked_files.split('\n')
		txt_files = [f for f in all_files if f.endswith('.txt')]

		if not txt_files:
			print("No uncommitted .txt files found.")
			return True

		# Process each file and store metadata
		metadata_files = []
		for file_path in txt_files:
			try:
				with open(file_path, 'r', encoding='utf-8') as f:
					content = f.read()

				metadata = extract_metadata(content, file_path)
				metadata_file = store_metadata(file_path, metadata)
				metadata_files.append(metadata_file)

				print(f"File: {file_path}")
				print(f"Author: {metadata['author']}")
				print(f"Title: {metadata['title']}")
				print(f"Hashtags: {', '.join(metadata['hashtags'])}")
				print(f"File Hash: {metadata['file_hash']}")
				print()
			except Exception as e:
				print(f"Error processing file {file_path}: {str(e)}")

		# Add all .txt files and metadata files to staging
		files_to_add = txt_files + metadata_files
		for file in files_to_add:
			run_git_command(f"git add {file}")

		# Create commit message
		commit_message = f"Auto-commit {len(txt_files)} text files and metadata on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by commit_files.py"

		# Commit the changes
		run_git_command(f'git commit -m "{commit_message}"')

		print(f"Committed {len(txt_files)} text files and their metadata.")
		print("Commit message:", commit_message)

		# Try to push changes if possible
		push_changes()

		return True

	except Exception as e:
		print(f"Error in commit_text_files: {str(e)}")
		return False
	finally:
		os.chdir(curr_dir)

if __name__ == "__main__":
	repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
	commit_text_files(repo_path=repo_path)

# end commit_files.py ; marker comment, please do not remove