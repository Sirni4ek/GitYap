# begin template/python3/outline.py ; marker comment, please do not remove

# outline.py
# Create an outline of Python code in a given directory.
# The outline includes imports, constants, variables, classes, and functions.

import ast
import os
import sys

def get_python_files(start_path):
	"""Recursively find all .py files in the given directory."""
	python_files = []
	for root, _, files in os.walk(start_path):
		for file in files:
			if file.endswith('.py'):
				python_files.append(os.path.join(root, file))
	return python_files

def parse_file(file_path):
	"""Parse a Python file and return its AST."""
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			return ast.parse(f.read())
	except Exception as e:
		print(f"Error parsing {file_path}: {e}")
		return None

def get_imports(tree):
	"""Extract import statements from AST."""
	imports = []
	for node in ast.walk(tree):
		if isinstance(node, ast.Import):
			for name in node.names:
				imports.append(f"import {name.name}")
		elif isinstance(node, ast.ImportFrom):
			module = node.module or ''
			for name in node.names:
				imports.append(f"from {module} import {name.name}")
	return imports

def get_assignments(tree):
	"""Extract top-level assignments and their types."""
	assignments = []
	for node in ast.walk(tree):
		if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
			target_name = node.targets[0].id
			value_type = "unknown"

			# Determine the type of the assigned value
			if isinstance(node.value, ast.Dict):
				value_type = "dict"
			elif isinstance(node.value, ast.List):
				value_type = "list"
			elif isinstance(node.value, ast.Str):
				value_type = "str"
			elif isinstance(node.value, ast.Call):
				if isinstance(node.value.func, ast.Name):
					value_type = node.value.func.id

			assignments.append(f"{target_name} ({value_type})")
	return assignments

def get_classes_and_functions(tree):
	"""Extract class and function definitions from AST."""
	classes = []
	functions = []

	for node in ast.walk(tree):
		if isinstance(node, ast.ClassDef):
			classes.append(node.name)
		elif isinstance(node, ast.FunctionDef):
			functions.append(node.name)

	return classes, functions

def create_outline(directory):
	"""Create an outline of all Python files in the directory."""
	files = get_python_files(directory)

	print("Code Outline")
	print("=" * 50)

	for file_path in files:
		relative_path = os.path.relpath(file_path, directory)
		print(f"\nFile: {relative_path}")
		print("-" * 50)

		tree = parse_file(file_path)
		if tree is None:
			continue

		imports = get_imports(tree)
		assignments = get_assignments(tree)
		classes, functions = get_classes_and_functions(tree)

		if imports:
			print("\nImports:")
			for imp in imports:
				print(f"  {imp}")

		if assignments:
			print("\nConstants and Variables:")
			for assignment in assignments:
				print(f"  {assignment}")

		if classes:
			print("\nClasses:")
			for cls in classes:
				print(f"  {cls}")

		if functions:
			print("\nFunctions:")
			for func in functions:
				print(f"  {func}")

		print("=" * 50)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python outline.py <directory>")
		sys.exit(1)
	directory = sys.argv[1]
	create_outline(directory)

# end outline.py ; marker comment, please do not remove