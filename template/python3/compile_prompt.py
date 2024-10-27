#!/usr/bin/env python3
# begin template/python3/compile_prompt.py ; marker comment, please do not remove

import os
import sys

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

def format_file_content(file_path, content):
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
        prefix_path = os.path.join(template_dir, 'txt', 'prompt_prefix.txt')
        suffix_path = os.path.join(template_dir, 'txt', 'prompt_suffix.txt')
        todo_path = os.path.join(template_dir, 'txt', 'todo.txt')

        try:
            prefix_content = read_file(prefix_path) if os.path.exists(prefix_path) else ""
            suffix_content = read_file(suffix_path) if os.path.exists(suffix_path) else ""
            todo_content = read_file(todo_path) if os.path.exists(todo_path) else ""
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

        # Walk through the template directory
        for root, dirs, files in os.walk(template_dir):
            for file in sorted(files):
                if file.startswith('.') or file in ['prompt_prefix.txt', 'prompt_suffix.txt', 'todo.txt']:
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path)

                try:
                    content = read_file(file_path)
                    formatted_content = format_file_content(relative_path, content)
                    output.append(formatted_content)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}", file=sys.stderr)
                    raise

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