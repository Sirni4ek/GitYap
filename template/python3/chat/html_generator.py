# begin template/python3/chat/html_generator.py
import os
from datetime import datetime, timezone
from multiprocessing import Pool
from functools import partial
from .file_reader import read_file, truncate_message
from .channel_manager import get_available_channels, get_channel_files
from .message_processor import process_file

def generate_chat_html(repo_path, output_file, channel='general', max_messages=50, max_message_length=300, title="Timble Chat"):
    HTML_TEMPLATE = read_file('./template/html/chat_page.html')
    MESSAGE_TEMPLATE = read_file('./template/html/chat_message.html')
    MESSAGE_FORM_TEMPLATE = read_file('./template/html/chat_message_form.html')

    channels = get_available_channels(repo_path)
    
    channel_nav = '<div class="channel-nav">'
    for ch in channels:
        active_class = 'active' if ch == channel else ''
        channel_nav += f'<a href="/chat/{ch}.html" class="channel-link {active_class}">{ch}</a>'
    channel_nav += '</div>'

    message_dir = os.path.join(repo_path, "message")
    file_paths = get_channel_files(message_dir, channel)

    with Pool() as pool:
        process_func = partial(process_file, repo_path=repo_path, target_channel=channel)
        messages = pool.map(process_func, file_paths)

    messages = [msg for msg in messages if msg is not None]
    messages.sort(key=lambda x: (-x['timestamp'].timestamp(), x['file_path']))
    messages = messages[:max_messages]

    chat_messages = []
    for idx, msg in enumerate(messages):
        truncated_content, is_truncated = truncate_message(msg['content'], max_message_length)
        expand_link = f'<a href="#" class="expand-link" data-message-id="{idx}">{"Show More" if is_truncated else ""}</a>'
        full_content = f'<div class="full-message" id="full-message-{idx}" style="display: none;">{msg["content"]}</div>' if is_truncated else ''

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
# end template/python3/chat/html_generator.py


