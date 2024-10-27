#!/usr/bin/env python3
# begin template/python3/file_utils.py ; marker comment, please do not remove

import os
import chardet

class FileUtils:
	@staticmethod
	def read_file_safe(file_path, default_encoding='utf-8'):
		try:
			with open(file_path, 'rb') as f:
				raw_data = f.read()
			detected_encoding = chardet.detect(raw_data)['encoding'] or default_encoding
			return raw_data.decode(detected_encoding)
		except Exception as e:
			print(f"Error reading file {file_path}: {str(e)}")
			return None

	@staticmethod
	def write_file_safe(file_path, content, encoding='utf-8'):
		try:
			os.makedirs(os.path.dirname(file_path), exist_ok=True)
			with open(file_path, 'w', encoding=encoding) as f:
				f.write(content)
			return True
		except Exception as e:
			print(f"Error writing file {file_path}: {str(e)}")
			return False

# end template/python3/file_utils.py ; marker comment, please do not remove