/* begin template/js/chat.js ; marker comment, please do not remove */
document.addEventListener('DOMContentLoaded', function() {
	document.querySelectorAll('.expand-link').forEach(function(link) {
		link.addEventListener('click', function(e) {
			e.preventDefault();
			var messageId = this.getAttribute('data-message-id');
			var fullMessage = document.getElementById('full-message-' + messageId);
			if (fullMessage) {
				fullMessage.style.display = 'block';
				this.style.display = 'none';
			}
		});
	});
	const searchInput = document.getElementById('message-search');
	if (searchInput) {
		const performSearch = debounce((e) => {
			const searchTerm = e.target.value.toLowerCase();
			const messages = document.querySelectorAll('.message');

			messages.forEach(message => {
				const content = message.querySelector('.message-content').textContent.toLowerCase();
				const author = message.querySelector('.author').textContent.toLowerCase();
				const hashtags = message.querySelector('.hashtags').textContent.toLowerCase();

				const matches = content.includes(searchTerm) ||
					author.includes(searchTerm) ||
					hashtags.includes(searchTerm);

				message.style.display = matches ? 'block' : 'none';
				message.classList.toggle('message-highlight', matches && searchTerm);
			});
		}, 300);

		searchInput.addEventListener('input', performSearch);
		searchInput.addEventListener('keydown', function(e) {
			if (e.key === 'Escape') {
				this.value = '';
				this.dispatchEvent(new Event('input'));
			}
		});
	}
});

async function postMessage(event) {
	event.preventDefault();
	const form = event.target;
	const data = {
		content: form.content.value,
		author: form.author.value,
		tags: form.tags.value.split(' ').filter(t => t).map(t => t.startsWith('#') ? t : '#' + t),
		reply_to: form.reply_to?.value || null
	};

	try {
		const response = await fetch('/post', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify(data)
		});

		if (!response.ok) throw new Error(await response.text());

		form.reset();
		// Add a small delay before reloading to ensure the server has time to process
		setTimeout(() => {
			window.location.reload();
		}, 500);
	} catch (error) {
		alert('Error posting message: ' + error.message);
	}
	return false;
}

function debounce(func, wait) {
	let timeout;
	return function executedFunction(...args) {
		const later = () => {
			clearTimeout(timeout);
			func(...args);
		};
		clearTimeout(timeout);
		timeout = setTimeout(later, wait);
	};
}

function replyToMessage(messageId, author) {
	const textarea = document.querySelector('textarea[name="content"]');
	const replyToInput = document.querySelector('input[name="reply_to"]');

	// Focus the textarea
	textarea.focus();

	// Set the reply_to field
	if (replyToInput) {
		replyToInput.value = messageId;
	}

	// Add a visual indicator in the textarea
	textarea.value = `@${author} ` + textarea.value;
}

// Add form expansion functionality
document.addEventListener('DOMContentLoaded', function() {
	const messageForm = document.getElementById('post-form');
	const textarea = messageForm.querySelector('textarea');

	textarea.addEventListener('focus', function() {
		messageForm.classList.add('expanded');
	});

	// Optional: Collapse form when clicking outside
	document.addEventListener('click', function(e) {
		if (!messageForm.contains(e.target)) {
			messageForm.classList.remove('expanded');
		}
	});

	// Store and restore author name
	const authorInput = messageForm.querySelector('input[name="author"]');
	if (authorInput) {
		// Restore saved author name
		const savedAuthor = localStorage.getItem('authorName');
		if (savedAuthor) {
			authorInput.value = savedAuthor;
		}

		// Save author name when changed
		authorInput.addEventListener('change', function() {
			localStorage.setItem('authorName', this.value);
		});
	}
});

/* end chat.js ; marker comment, please do not remove */