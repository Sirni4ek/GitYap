# begin template/python3/chat.html.py
import argparse
from chat.html_generator import generate_chat_html
from chat.file_reader import DEBUG

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

	repo_path = "."
	# Remove the output filename modification
	output_file = args.output_file

	generate_chat_html(
		repo_path=repo_path,
		output_file=output_file,
		channel=args.channel,
		max_messages=args.max_messages,
		max_message_length=args.max_message_length,
		title=args.title
	)
# end chat.html.py