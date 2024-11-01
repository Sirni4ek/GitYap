/* begin template/js/chat.js ; marker comment, please do not remove */
console.log("chat.js loading...");  // Add this at the very top of the file

class ChatClient {
	constructor() {
		console.log("ChatClient constructor called");
		this.ws = null;
		this.connect();
		this.setupReconnection();
		this.setupFormHandler();
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

	setupFormHandler() {
		console.log("Setting up form handler");
		const form = document.getElementById('post-form');
		console.log("Form found:", form);  // This will show null if form not found
		if (!form) return;

		form.addEventListener('submit', async (event) => {
			console.log("Form submit event triggered");
			event.preventDefault();  // This should be first
			console.log('Form submission intercepted');
	
			// Get form data
			const formData = new FormData(form);
			const data = Object.fromEntries(formData.entries());
			console.log('Form data:', data);  // Debug log
	
			// Show loading state
			const submitButton = form.querySelector('button[type="submit"]');
			const originalText = submitButton.textContent;
			submitButton.disabled = true;
			submitButton.textContent = 'Sending...';
	
			// Get channel from URL or default to 'general'
			const channel = window.location.pathname.split('/').pop().replace('.html', '') || 'general';
	
			try {
				// Prepare the payload with safer data handling
				const payload = {
					content: (data.content || '').trim(),
					author: (data.author || 'Guest').trim(),
					tags: data.tags ? data.tags.split(/[,\s]+/).filter(tag => tag) : [],
					channel: channel,
					reply_to: data.reply_to || null
				};
	
				console.log('Prepared payload:', payload);  // Debug log
				console.log('Stringified payload:', JSON.stringify(payload));  // Debug log
	
				// Send to server
				const response = await fetch('/post', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify(payload)
				});	

				// Get response text first for debugging
				const responseText = await response.text();
				console.log('Raw server response:', responseText);

				// Try to parse the response as JSON
				let responseData;
				try {
					responseData = JSON.parse(responseText);
				} catch (e) {
					throw new Error('Server returned invalid JSON: ' + responseText);
				}

				if (!response.ok) {
					throw new Error(responseData.error || 'Failed to post message');
				}

				// Add message to UI optimistically
				const messagesContainer = document.querySelector('.chat-messages');
				const messageHTML = this.createMessageHTML(payload);
				messagesContainer.insertAdjacentHTML('afterbegin', messageHTML);

				// Clear form
				form.reset();

				// Refresh messages to get proper IDs and formatting
				this.refreshMessages();

			} catch (error) {
				console.error('Error:', error);
				alert('Error posting message: ' + error.message);
			} finally {
				// Reset button state
				submitButton.disabled = false;
				submitButton.textContent = originalText;
			}
		});
	}

	handleNewMessage(message) {
		const messagesContainer = document.querySelector('.chat-messages');
		if (messagesContainer) {
			messagesContainer.insertAdjacentHTML('afterbegin', message);
		}
	}

	refreshMessages() {
		fetch(window.location.href)
			.then(response => response.text())
			.then(html => {
				const parser = new DOMParser();
				const doc = parser.parseFromString(html, 'text/html');
				const newMessages = doc.querySelector('.chat-messages');
				const currentMessages = document.querySelector('.chat-messages');
				if (newMessages && currentMessages) {
					currentMessages.innerHTML = newMessages.innerHTML;
				}
			})
			.catch(error => console.error('Error refreshing messages:', error));
	}

	createMessageHTML(messageData) {
		const now = new Date().toISOString();
		const tags = Array.isArray(messageData.tags)
			? messageData.tags.join(' ')
			: (messageData.tags || '');

		return `
			<div class="message">
				<div class="message-header">
					<span class="author">${messageData.author || 'Guest'}</span>
				</div>
				<div class="message-content">
					${messageData.content}
				</div>
				<div class="hashtags">${tags}</div>
				<button class="reply-button" onclick="replyToMessage('temp-${now}', '${messageData.author}')" title="Reply to this message">
					Reply
				</button>
			</div>
		`;
	}
}

function setupSearch() {
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
}

function setupSyncButton() {
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
						channel: window.location.pathname.split('/').pop().replace('.html', '') || 'general'
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
}

function initializeFormControls() {
	const form = document.getElementById('post-form');
	if (!form) return;

	const optionalFields = form.querySelector('.optional-fields');
	const authorInput = form.querySelector('input[name="author"]');

	// Add toggle buttons
	const controls = document.createElement('div');
	controls.className = 'form-controls';
	controls.innerHTML = '';
	form.appendChild(controls);

	// Load saved preferences
	const showOptionalFields = localStorage.getItem('showOptionalFields') === 'true';
	if (showOptionalFields) {
		optionalFields?.classList.add('visible');
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
			optionalFields?.classList.toggle('visible', anyActive);

			// Save preference
			localStorage.setItem('showOptionalFields', anyActive ? 'true' : 'false');
		}
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
	textarea?.focus();

	// Set the reply_to field
	if (replyToInput) {
		replyToInput.value = messageId;
	}

	// Add a visual indicator in the textarea
	if (textarea) {
		textarea.value = `@${author} ` + textarea.value;
	}
}

document.addEventListener('DOMContentLoaded', function() {
	console.log("DOMContentLoaded event fired");
	// Initialize chat client
	window.chatClient = new ChatClient();
	console.log("ChatClient initialized");

	// Initialize form controls once
	initializeFormControls();

	// Setup search functionality once
	setupSearch();

	// Focus message input
	document.getElementById('message')?.focus();

	// Setup sync button
	setupSyncButton();
});

/* end chat.js ; marker comment, please do not remove */
