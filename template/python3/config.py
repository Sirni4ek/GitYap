# begin template/python3/config.py ; marker comment, please do not remove

# Configuration constants
SCRIPT_TYPES = ['py', 'pl', 'rb', 'sh', 'js']
INTERPRETERS = ['python3', 'perl', 'ruby', 'bash', 'node']
INTERPRETER_MAP = dict(zip(SCRIPT_TYPES, INTERPRETERS))
MIME_TYPES = {
	'txt': 'text/plain',
	'html': 'text/html',
	'css': 'text/css',
	'js': 'application/javascript',
	'json': 'application/json',
	'png': 'image/png',
	'jpg': 'image/jpeg',
	'gif': 'image/gif',
}

# end config.py ; marker comment, please do not remove