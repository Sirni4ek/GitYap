# begin template/python3/chat/message_processor.py
import os
import re
from datetime import datetime, timezone
from .file_reader import read_file, extract_metadata

def process_file(file_path, repo_path, target_channel='general'):
    relative_path = os.path.relpath(file_path, repo_path)
    try:
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
        content = read_file(file_path)
        author, hashtags = extract_metadata(content)

        # Extract channel from content or directory structure
        channel_match = re.search(r'Channel:\s*(.+)', content)
        if channel_match:
            channel = channel_match.group(1)
        else:
            channel = os.path.basename(os.path.dirname(file_path))

        # Extract reply_to if it exists
        reply_to = None
        reply_match = re.search(r'Reply-To:\s*(.+)', content)
        if reply_match:
            reply_to = reply_match.group(1)

        content = re.sub(r'(author|channel|reply-to):\s*.+', '', content, flags=re.IGNORECASE).strip()

        if target_channel == 'everything' or channel == target_channel:
            return {
                'author': author,
                'content': content,
                'timestamp': modification_time,
                'hashtags': hashtags,
                'channel': channel,
                'file_path': file_path,
                'message_id': os.path.splitext(os.path.basename(file_path))[0],
                'reply_to': reply_to
            }
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None
# end template/python3/chat/message_processor.py


