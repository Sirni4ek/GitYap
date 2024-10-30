# begin template/python3/chat/channel_manager.py
import os

def get_available_channels(repo_path):
    """Get list of available channels from message directory structure"""
    message_dir = os.path.join(repo_path, "message")
    if not os.path.exists(message_dir):
        os.makedirs(message_dir)
        os.makedirs(os.path.join(message_dir, "general"))
        return ["everything", "general"]

    channels = ["everything"]  # Always include "everything" channel
    for item in os.listdir(message_dir):
        if os.path.isdir(os.path.join(message_dir, item)):
            channels.append(item)
    return channels if len(channels) > 1 else ["everything", "general"]

def get_channel_files(message_dir, channel):
    if channel == 'everything':
        file_paths = []
        for root, _, files in os.walk(message_dir):
            for file in files:
                if file.endswith(".txt"):
                    file_paths.append(os.path.join(root, file))
    else:
        channel_dir = os.path.join(message_dir, channel)
        if not os.path.exists(channel_dir):
            os.makedirs(channel_dir)

        file_paths = []
        for root, _, files in os.walk(channel_dir):
            for file in files:
                if file.endswith(".txt"):
                    file_paths.append(os.path.join(root, file))
    return file_paths
# end template/python3/chat/channel_manager.py


