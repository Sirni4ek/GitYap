#!/usr/bin/env python3
# begin template/python3/compile_prompt.py ; marker comment, please do not remove

import os
import sys
import re

def get_file_stats(file_path):
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			content = f.read()
			lines = content.count('\n') + 1
			size = os.path.getsize(file_path)
			return {
				'lines': lines,
				'size': size,
				'type': os.path.splitext(file_path)[1][1:]
			}
	except Exception as e:
		print(f"Error getting stats for {file_path}: {e}", file=sys.stderr)
		return {'lines': 0, 'size': 0, 'type': 'unknown'}

def format_size(size):
	for unit in ['B', 'KB', 'MB']:
		if size < 1024:
			return f"{size:.1f}{unit}"
		size /= 1024
	return f"{size:.1f}GB"

def read_file(file_path):
	encodings = ['utf-8', 'latin-1']
	for encoding in encodings:
		try:
			with open(file_path, 'r', encoding=encoding) as f:
				return f.read()
		except UnicodeDecodeError:
			continue
		except IOError as e:
			print(f"Error reading file {file_path}: {e}", file=sys.stderr)
			raise
	raise UnicodeDecodeError(f"Could not read {file_path} with any supported encoding")

def has_marker_comments(content, file_path):
	# Define patterns for different comment styles
	patterns = {
		'hash': (f"# begin {file_path} ; marker comment, please do not remove",
				f"# end {os.path.basename(file_path)} ; marker comment, please do not remove"),
		'c_style': (f"/\\* begin {file_path} ; marker comment, please do not remove \\*/",
				   f"/\\* end {os.path.basename(file_path)} ; marker comment, please do not remove \\*/"),
		'html': (f"<!-- begin {file_path} ; marker comment, please do not remove -->",
				f"<!-- end {os.path.basename(file_path)} ; marker comment, please do not remove -->")
	}

	for begin_pattern, end_pattern in patterns.values():
		if (re.search(begin_pattern, content[:500]) and  # Check only first 500 chars for begin
			re.search(end_pattern, content[-500:])):     # Check only last 500 chars for end
			return True
	return False

def format_file_content(file_path, content):
	if has_marker_comments(content, file_path):
		return content

	ext = os.path.splitext(file_path)[1].lower()

	if ext in ['.py', '.sh', '.rb', '.pl']:
		marker = '#'
	elif ext in ['.js', '.css']:
		return f"/* begin {file_path} ; marker comment, please do not remove */\n{content}\n/* end {os.path.basename(file_path)} ; marker comment, please do not remove */\n"
	elif ext in ['.html']:
		return f"<!-- begin {file_path} ; marker comment, please do not remove -->\n{content}\n<!-- end {os.path.basename(file_path)} ; marker comment, please do not remove -->\n"
	else:
		marker = '#'

	return f"{marker} begin {file_path} ; marker comment, please do not remove\n{content}\n{marker} end {os.path.basename(file_path)} ; marker comment, please do not remove\n"

def compile_prompt(template_dir='template'):
	try:
		if not os.path.exists(template_dir):
			raise FileNotFoundError(f"Template directory '{template_dir}' not found")

		# Read template files
		prefix_path = os.path.join(template_dir, 'txt', 'prompt_process_todo.txt')
		suffix_path = os.path.join(template_dir, 'txt', 'prompt_suffix.txt')
		outline_path = os.path.join('doc', 'outline.txt')
		todo_path = os.path.join('doc', 'todo.txt')

		try:
			prefix_content = read_file(prefix_path) if os.path.exists(prefix_path) else ""
			suffix_content = read_file(suffix_path) if os.path.exists(suffix_path) else ""
			todo_content = read_file(todo_path) if os.path.exists(todo_path) else ""
			outline_content = read_file(outline_path) if os.path.exists(outline_path) else ""
		except Exception as e:
			print(f"Error reading template files: {e}", file=sys.stderr)
			raise

		output = []

		# Add prefix if it exists
		if prefix_content:
			output.append(prefix_content)

		# Add todo content if it exists
		if todo_content:
			output.append("\nTODO List:")
			output.append(todo_content)
			output.append("\nSource Files:")
			output.append(outline_content)

		# Add file statistics summary before the source files
		output.append("\nFile Statistics:")
		total_lines = 0
		total_size = 0
		file_stats = []

		for root, dirs, files in os.walk(template_dir):
			for file in sorted(files):
				if file.startswith('.') or file in ['prompt_process_todo.txt', 'prompt_suffix.txt', 'todo.txt']:
					continue

				# exclude .pyc files and __pycache__ directories
				if file.endswith('.pyc') or '__pycache__' in root:
					continue

				file_path = os.path.join(root, file)
				relative_path = os.path.relpath(file_path)
				stats = get_file_stats(file_path)

				file_stats.append(f"{relative_path}: {stats['lines']} lines, {format_size(stats['size'])}, {stats['type']} file")
				total_lines += stats['lines']
				total_size += stats['size']

		output.append(f"\nTotal Files: {len(file_stats)}")
		output.append(f"Total Lines: {total_lines}")
		output.append(f"Total Size: {format_size(total_size)}\n")
		output.append("Individual Files:")
		output.extend(file_stats)

		# Add suffix if it exists
		if suffix_content:
			output.append(suffix_content)

		# Write to prompt.txt
		try:
			with open('prompt.txt', 'w', encoding='utf-8') as f:
				f.write('\n'.join(output))

			print(f"Prompt compiled to prompt.txt")
			print(f"Total files included: {len(output)}")

		except IOError as e:
			print(f"Error writing prompt.txt: {e}", file=sys.stderr)
			raise

	except Exception as e:
		print(f"Error during prompt compilation: {e}", file=sys.stderr)
		raise

if __name__ == "__main__":
	compile_prompt()

# end compile_prompt.py ; marker comment, please do not remove