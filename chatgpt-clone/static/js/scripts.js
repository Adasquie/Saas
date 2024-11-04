document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const themeToggle = document.getElementById('theme-toggle');

    // Function to toggle theme
    function toggleTheme() {
        document.body.classList.toggle('light-mode');
        document.querySelector('.chat-container').classList.toggle('light-mode');
        document.querySelector('.chat-header').classList.toggle('light-mode');
        chatWindow.classList.toggle('light-mode');
        document.querySelector('.chat-input-area').classList.toggle('light-mode');
        document.querySelector('.chat-footer')?.classList.toggle('light-mode'); // If footer exists

        // Change toggle button icon
        if (document.body.classList.contains('light-mode')) {
            themeToggle.innerText = '☀️';
        } else {
            themeToggle.innerText = '🌙';
        }
    }

    // Event listener for theme toggle button
    themeToggle.addEventListener('click', toggleTheme);
    // Function to append messages to the chat window
    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);

        const textDiv = document.createElement('div');
        textDiv.classList.add('text');

        const messageContent = document.createElement('p');
        messageContent.innerText = text;

        const timestamp = document.createElement('span');
        timestamp.classList.add('timestamp');
        const now = new Date();
        timestamp.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        textDiv.appendChild(messageContent);
        textDiv.appendChild(timestamp);
        messageDiv.appendChild(textDiv);
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Function to handle sending messages
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
    
        appendMessage('user', message);
        userInput.value = '';
        userInput.focus();
    
        // Disable send button and input
        sendBtn.disabled = true;
        userInput.disabled = true;
        sendBtn.innerText = 'Sending...';
    
        // Show typing indicator
        showTypingIndicator();
    
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });
    
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
    
            const data = await response.json();
            removeTypingIndicator();
            appendMessage('ai', data.response);
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            appendMessage('ai', "Sorry, I couldn't process your request.");
        } finally {
            // Re-enable send button and input
            sendBtn.disabled = false;
            userInput.disabled = false;
            sendBtn.innerText = 'Send';
        }
    }

        // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'ai', 'typing');
        typingDiv.innerHTML = `<div class="text"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
        chatWindow.appendChild(typingDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.message.ai.typing');
        if (typingIndicator) {
            chatWindow.removeChild(typingIndicator);
        }
    }

    // Event listener for send button
    sendBtn.addEventListener('click', sendMessage);

    // Event listener for Enter key
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});