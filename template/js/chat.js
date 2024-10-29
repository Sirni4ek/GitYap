/* begin template/js/chat.js ; marker comment, please do not remove */

class ChatClient {
	constructor() {
		this.ws = null;
		this.connect();
		this.setupReconnection();
	}

	connect() {
		const wsPort = parseInt(window.location.port) + 1;
		this.ws = new WebSocket(`ws://localhost:${wsPort}`);

		this.ws.onmessage = (event) => {
			const data = JSON.parse(event.data);
			if (data.type === 'new_message') {
				this.handleNewMessage(data.message);
			} else if (data.type === 'update_required') {
				this.refreshMessages();
			}
		};
	}

	setupReconnection() {
		this.ws.onclose = () => {
			console.log('WebSocket closed, reconnecting...');
			setTimeout(() => this.connect(), 1000);
		};
	}

	handleNewMessage(message) {
		// Insert new message into DOM
		const messagesContainer = document.querySelector('.chat-messages');
		messagesContainer.insertAdjacentHTML('afterbegin', message);
	}

	refreshMessages() {
		// Reload messages without full page refresh
		fetch(window.location.href)
			.then(response => response.text())
			.then(html => {
				const parser = new DOMParser();
				const doc = parser.parseFromString(html, 'text/html');
				const newMessages = doc.querySelector('.chat-messages');
				document.querySelector('.chat-messages').innerHTML = newMessages.innerHTML;
			});
	}
}

document.addEventListener('DOMContentLoaded', function() {
	// Initialize form controls
	initializeFormControls();

	// Search functionality
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
	window.chatClient = new ChatClient();
	// if (form) {
	// 	// Remove the inline onsubmit handler and add it here
	// 	form.addEventListener('submit', async function(event) {
	// 		event.preventDefault(); // This must happen first
	// 		await postMessage(event);
	// 	});
	// }

	const form = document.getElementById('post-form');
	if (form) {
		console.log('Found post form'); // Debug log

		form.addEventListener('submit', function(event) {
			event.preventDefault(); // This is crucial - stop the default form submission
			console.log('Form submission intercepted'); // Debug log

			const formData = new FormData(form);
			const data = {};
			formData.forEach((value, key) => {
				data[key] = value;
			});

			// Show loading state
			const submitButton = form.querySelector('button[type="submit"]');
			const originalText = submitButton.textContent;
			submitButton.disabled = true;
			submitButton.textContent = 'Sending...';

			fetch('/post', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(data)
			})
				.then(response => {
					console.log('Response received:', response); // Debug log
					return response.json();
				})
				.then(data => {
					console.log('Processed data:', data); // Debug log
					if (data.error) {
						throw new Error(data.error);
					}
					// Clear the form
					form.reset();

					// Redirect to the chat page
					if (data.redirect) {
						window.location.href = data.redirect;
					}
				})
				.catch(error => {
					console.error('Error:', error); // Debug log
					alert('Error posting message: ' + error.message);
				})
				.finally(() => {
					// Reset button state
					submitButton.disabled = false;
					submitButton.textContent = originalText;
				});
		});
	} else {
		console.log('Post form not found'); // Debug log
	}
	document.getElementById('message').focus();

	const syncButton = document.getElementById('sync-button');
	if (syncButton) {
		syncButton.addEventListener('click', async function() {
			this.disabled = true;
			const originalText = this.textContent;
			this.textContent = 'Syncing...';

			try {
				const response = await fetch('/sync', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						channel: window.location.pathname.split('/').pop().replace('.html', '')
					})
				});

				if (!response.ok) {
					throw new Error('Sync failed');
				}

				// Refresh messages after successful sync
				window.chatClient.refreshMessages();
			} catch (error) {
				console.error('Sync error:', error);
				alert('Error syncing messages: ' + error.message);
			} finally {
				this.disabled = false;
				this.textContent = originalText;
			}
		});
	}
});

function initializeFormControls() {
	const form = document.getElementById('post-form');
	const optionalFields = form.querySelector('.optional-fields');
	const authorInput = form.querySelector('input[name="author"]');

	// Add toggle buttons
	const controls = document.createElement('div');
	controls.className = 'form-controls';
	controls.innerHTML = '';
	// controls.innerHTML = `
	// 	<button type="button" class="form-toggle" data-field="author">
	// 		<span class="toggle-icon">Options</span>
	// 	</button>
	// `;
	form.appendChild(controls);

	// Load saved preferences
	const showOptionalFields = localStorage.getItem('showOptionalFields') === 'true';
	if (showOptionalFields) {
		optionalFields.classList.add('visible');
		controls.querySelectorAll('.form-toggle').forEach(btn => btn.classList.add('active'));
	}

	// Load saved author name
	const savedAuthor = localStorage.getItem('authorName');
	if (savedAuthor) {
		authorInput.value = savedAuthor;
	}

	// Toggle button handlers
	controls.addEventListener('click', (e) => {
		if (e.target.closest('.form-toggle')) {
			const button = e.target.closest('.form-toggle');
			button.classList.toggle('active');

			// Update visibility of optional fields
			const anyActive = controls.querySelector('.form-toggle.active');
			optionalFields.classList.toggle('visible', anyActive);

			// Save preference
			localStorage.setItem('showOptionalFields', anyActive ? 'true' : 'false');
		}
	});
}

function postMessage(event) {
	event.preventDefault();

	const form = event.target;
	const formData = new FormData(form);
	const data = {};

	// Convert FormData to plain object
	for (let [key, value] of formData.entries()) {
		data[key] = value;
	}

	// Show loading state
	const submitButton = form.querySelector('button[type="submit"]');
	const originalText = submitButton.textContent;
	submitButton.disabled = true;
	submitButton.textContent = 'Sending...';

	// Send the message
	fetch('/post', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(data)
	})
		.then(response => response.json())
		.then(data => {
			if (data.error) {
				throw new Error(data.error);
			}
			// Clear the form
			form.reset();

			// Redirect to the chat page
			if (data.redirect) {
				window.location.href = data.redirect;
			}
		})
		.catch(error => {
			alert('Error posting message: ' + error.message);
		})
		.finally(() => {
			// Reset button state
			submitButton.disabled = false;
			submitButton.textContent = originalText;
		});
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

/* end chat.js ; marker comment, please do not remove */
