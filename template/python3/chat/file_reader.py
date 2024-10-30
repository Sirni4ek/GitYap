# begin template/python3/chat/file_reader.py
import chardet
import re

DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def read_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        detected_encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
        return raw_data.decode(detected_encoding)
    except Exception as e:
        debug_print(f"Error reading file {file_path}: {str(e)}")
        return ""

# Compile regular expressions once
author_regex = re.compile(r'Author:\s*(.+)', re.IGNORECASE)
hashtag_regex = re.compile(r'#\w+')

def extract_metadata(content):
    author = author_regex.search(content)
    author = author.group(1) if author else "Unknown"
    hashtags = hashtag_regex.findall(content)
    return author, hashtags

def truncate_message(content, max_length=300):
    if len(content) <= max_length:
        return content, False
    return content[:max_length] + "...", True
# end template/python3/chat/file_reader.py


