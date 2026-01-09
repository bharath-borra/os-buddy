let currentSessionId = null;

document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const historyList = document.getElementById('history-list');

    // 1. Initial Load: Fetch Sessions
    fetchSessions();

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    sendBtn.addEventListener('click', sendMessage);
});

async function fetchSessions() {
    try {
        const res = await fetch('/sessions');
        const sessions = await res.json();
        renderHistoryList(sessions);
    } catch (e) {
        console.error("Failed to fetch sessions", e);
    }
}

function renderHistoryList(sessions) {
    const historyList = document.getElementById('history-list');
    if (!historyList) return;
    historyList.innerHTML = ''; // Clear

    // Always add "New Chat" at top
    const newChatLi = document.createElement('li');
    newChatLi.textContent = "+ New Chat";
    newChatLi.classList.add('new-chat-btn');
    newChatLi.onclick = startNewChat;
    historyList.appendChild(newChatLi);

    sessions.forEach(session => {
        const li = document.createElement('li');
        li.textContent = session.title;
        if (session.id === currentSessionId) li.classList.add('active');
        li.onclick = () => loadSession(session.id);
        historyList.appendChild(li);
    });
}

async function startNewChat() {
    currentSessionId = null; // Reset
    document.getElementById('messages-container').innerHTML = `
        <div class="message ai-message">
            <div class="avatar">AI</div>
            <div class="content">Hello! I'm OS Buddy. Ready for a new topic?</div>
        </div>
    `;
    fetchSessions(); // Refresh list to highlight selection
}

async function loadSession(sessionId) {
    currentSessionId = sessionId;
    // Fetch History
    try {
        const res = await fetch(`/sessions/${sessionId}`);
        const data = await res.json();

        // Render Messages
        const container = document.getElementById('messages-container');
        container.innerHTML = '';

        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => {
                appendMessage(msg.role === 'user' ? 'user-message' : 'ai-message', msg.content);
            });
        } else {
            container.innerHTML = `
                <div class="message ai-message">
                    <div class="avatar">AI</div>
                    <div class="content">This chat is empty.</div>
                </div>
            `;
        }
        fetchSessions(); // Update active state
    } catch (e) {
        console.error(e);
    }
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;

    // UI
    appendMessage('user-message', message);
    input.value = '';

    // Loading Indicator
    const loadingId = appendMessage('ai-message', 'Thinking...');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });
        const data = await response.json();

        // Remove loading
        removeMessage(loadingId);

        // Update Session ID if it was new
        if (data.session_id) {
            currentSessionId = data.session_id;
            fetchSessions(); // Refresh title in sidebar
        }

        appendMessage('ai-message', data.response);

    } catch (error) {
        removeMessage(loadingId);
        appendMessage('ai-message', "Error: Could not connect to OS Buddy.");
    }
}

function appendMessage(type, text) {
    const container = document.getElementById('messages-container');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.id = 'msg-' + Date.now();

    // Markdown parsing (simple)
    // If we have marked.js, use it
    let contentHtml = text;
    if (typeof marked !== 'undefined' && type === 'ai-message') {
        contentHtml = marked.parse(text);
    }

    msgDiv.innerHTML = `
        <div class="avatar">${type === 'user-message' ? 'U' : 'AI'}</div>
        <div class="content">${contentHtml}</div>
    `;

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
    return msgDiv.id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}
