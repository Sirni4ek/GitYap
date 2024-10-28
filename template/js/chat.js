/* begin template/js/chat.js ; marker comment, please do not remove */
document.addEventListener('DOMContentLoaded', function() {
	// Initialize form controls
	initializeFormControls();

	// Add form submit handler
	const form = document.getElementById('post-form');
	if (form) {
		// Remove the inline onsubmit handler and add it here
		form.addEventListener('submit', async function(event) {
			event.preventDefault(); // This must happen first
			await postMessage(event);
		});
	}

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
	document.getElementById('message').focus();
});

function initializeFormControls() {
	const form = document.getElementById('post-form');
	const optionalFields = form.querySelector('.optional-fields');
	const authorInput = form.querySelector('input[name="author"]');

	// Add toggle buttons
	const controls = document.createElement('div');
	controls.className = 'form-controls';
	controls.innerHTML = `
		<button type="button" class="form-toggle" data-field="author">
			<span class="toggle-icon">Options</span>
		</button>
	`;
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

async function postMessage(event) {
	event.preventDefault();

	const form = event.target;
	if (!form || form.id !== 'post-form') return false;

	// Validate required content
	const content = form.content.value.trim();
	if (!content) {
		alert('Please enter a message');
		return false;
	}

	// Get author name, defaulting to "Guest" if empty
	let author = form.author.value.trim() || "Guest";

	// Save author name to localStorage
	localStorage.setItem('authorName', author);

	// Get channel name from hidden input, default to 'general'
	const channel = (form.channel.value || 'general').trim()
		.replace(/[^a-zA-Z0-9_-]/g, ''); // Sanitize channel name

	const data = {
		content: content,
		author: author,
		tags: form.tags.value.split(' ')
			.filter(t => t)
			.map(t => t.startsWith('#') ? t : '#' + t),
		reply_to: form.reply_to?.value || null,
		channel: channel
	};

	try {
		// Show loading state
		const submitButton = form.querySelector('button[type="submit"]');
		const originalButtonText = submitButton.textContent;
		submitButton.textContent = 'Sending...';
		submitButton.disabled = true;

		// Ensure the Content-Type header is properly set
		console.log('Sending request with data:', data); // Debug log
		const response = await fetch('/post', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json;charset=UTF-8',
				'Accept': 'application/json'
			},
			body: JSON.stringify(data)
		});

		console.log('Response status:', response.status); // Debug log

		if (!response.ok) {
			const errorText = await response.text();
			console.log('Error response:', errorText); // Debug log
			throw new Error(errorText);
		}

		const result = await response.json();
		console.log('Success response:', result); // Debug log

		// Clear form fields
		form.content.value = '';
		form.tags.value = '';
		form.reply_to.value = '';

		// Reset button state
		submitButton.textContent = originalButtonText;
		submitButton.disabled = false;

		// Instead of redirecting, reload the current page
		window.location.reload();

	} catch (error) {
		console.error('Error posting message:', error);
		alert('Error posting message: ' + error.message);

		// Reset button state in case of error
		if (submitButton) {
			submitButton.textContent = originalButtonText;
			submitButton.disabled = false;
		}
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

/* end chat.js ; marker comment, please do not remove */
