# begin template/python3/chat.html.py ; marker comment, please do not remove

import os
import re
from datetime import datetime, timezone
import chardet
import argparse
from multiprocessing import Pool
from functools import partial

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
		print(f"Error reading file {file_path}: {str(e)}")
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

def get_available_channels(repo_path):
	"""Get list of available channels from message directory structure"""
	message_dir = os.path.join(repo_path, "message")
	if not os.path.exists(message_dir):
		os.makedirs(message_dir)
		os.makedirs(os.path.join(message_dir, "general"))
		return ["general"]

	channels = []
	for item in os.listdir(message_dir):
		if os.path.isdir(os.path.join(message_dir, item)):
			channels.append(item)
	return channels if channels else ["general"]

def process_file(file_path, repo_path):
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
			# Extract channel from directory path
			channel = os.path.basename(os.path.dirname(file_path))

		# Extract reply_to if it exists
		reply_to = None
		reply_match = re.search(r'Reply-To:\s*(.+)', content)
		if reply_match:
			reply_to = reply_match.group(1)

		content = re.sub(r'(author|channel|reply-to):\s*.+', '', content, flags=re.IGNORECASE).strip()

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
	except Exception as e:
		debug_print(f"Error reading file {file_path}: {str(e)}")
		return None

def generate_chat_html(repo_path, output_file, channel='general', max_messages=50, max_message_length=300, title="Timble Chat"):
	HTML_TEMPLATE = read_file('./template/html/chat_page.html')
	MESSAGE_TEMPLATE = read_file('./template/html/chat_message.html')
	MESSAGE_FORM_TEMPLATE = read_file('./template/html/chat_message_form.html')

	# Get list of all channels
	channels = get_available_channels(repo_path)

	# Build channel navigation HTML
	channel_nav = '<div class="channel-nav">'
	for ch in channels:
		active_class = 'active' if ch == channel else ''
		channel_nav += f'<a href="/chat/{ch}.html" class="channel-link {active_class}">{ch}</a>'
	channel_nav += '</div>'

	message_dir = os.path.join(repo_path, "message", channel)
	if not os.path.exists(message_dir):
		os.makedirs(message_dir)

	file_paths = []
	for root, _, files in os.walk(message_dir):
		for file in files:
			if file.endswith(".txt"):
				file_paths.append(os.path.join(root, file))

	with Pool() as pool:
		messages = pool.map(partial(process_file, repo_path=repo_path), file_paths)

	messages = [msg for msg in messages if msg is not None and msg['channel'] == channel]
	messages.sort(key=lambda x: (-x['timestamp'].timestamp(), x['file_path']))
	messages = messages[:max_messages]

	chat_messages = []
	for idx, msg in enumerate(messages):
		truncated_content, is_truncated = truncate_message(msg['content'], max_message_length)
		expand_link = f'<a href="#" class="expand-link" data-message-id="{idx}">{"Show More" if is_truncated else ""}</a>'
		full_content = f'<div class="full-message" id="full-message-{idx}" style="display: none;">{msg["content"]}</div>' if is_truncated else ''

		# Add reply-related fields
		reply_class = 'reply' if msg.get('reply_to') else ''
		reply_to = f'<div class="reply-to">Replying to: {msg["reply_to"]}</div>' if msg.get('reply_to') else ''

		message_html = MESSAGE_TEMPLATE.format(
			author=msg['author'],
			content=truncated_content,
			full_content=full_content,
			expand_link=expand_link,
			timestamp=msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
			hashtags=' '.join(msg['hashtags']),
			message_id=msg['message_id'],
			reply_class=reply_class,
			reply_to=reply_to
		)
		chat_messages.append(message_html)

	# Format the message form with the current channel
	message_form = MESSAGE_FORM_TEMPLATE.format(
		current_channel=channel
	)

	html_content = HTML_TEMPLATE.format(
		chat_messages=''.join(chat_messages),
		message_count=len(messages),
		current_time=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
		title=f"{title} - #{channel}",
		channel_nav=channel_nav,
		message_form=message_form
	)

	with open(output_file, 'w', encoding='utf-8') as f:
		f.write(html_content)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate chat HTML from repository messages.")
	parser.add_argument("--channel", type=str, default="general", help="Channel to display")
	parser.add_argument("--output_file", default="chat.html", help="Output HTML file name")
	parser.add_argument("--max_messages", type=int, default=50, help="Maximum number of messages to display")
	parser.add_argument("--max_message_length", type=int, default=300, help="Maximum length of each message before truncation")
	parser.add_argument("--title", default="Timble Chat", help="Title of the chat page")
	parser.add_argument("--debug", action="store_true", help="Enable debug output")

	args = parser.parse_args()
	DEBUG = args.debug

	# Use current directory as repo path
	repo_path = "."

	# Modify output file to include channel name
	output_file = args.output_file.replace('.html', f'_{args.channel}.html')

	generate_chat_html(
		repo_path=repo_path,
		output_file=output_file,
		channel=args.channel,
		max_messages=args.max_messages,
		max_message_length=args.max_message_length,
		title=args.title
	)

# end chat.html.py ; marker comment, please do not remove