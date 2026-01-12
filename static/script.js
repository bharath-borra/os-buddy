let currentSessionId = null;

// Get or Create User ID (Isolation)
function getUserId() {
    let userId = localStorage.getItem("os_buddy_user_id");
    if (!userId) {
        userId = "user_" + Math.random().toString(36).substr(2, 9);
        localStorage.setItem("os_buddy_user_id", userId);
    }
    return userId;
}

document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const historyList = document.getElementById('history-list');

    // Mobile Menu Logic
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('overlay');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }

    // 1. Initial Load: Fetch Sessions
    fetchSessions();

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    sendBtn.addEventListener('click', sendMessage);
});

async function fetchSessions() {
    try {
        const res = await fetch('/sessions', {
            headers: { 'X-User-ID': getUserId() }
        });
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

        // Chat Title
        const titleSpan = document.createElement('span');
        titleSpan.textContent = session.title;
        titleSpan.classList.add('chat-title');
        titleSpan.onclick = () => loadSession(session.id);

        // Delete Button
        const delBtn = document.createElement('span');
        delBtn.innerHTML = '&times;'; // Simple 'x' or use SVG
        delBtn.classList.add('delete-btn');
        delBtn.onclick = (e) => {
            e.stopPropagation(); // Stop click from loading session
            deleteSession(session.id);
        };

        li.appendChild(titleSpan);
        li.appendChild(delBtn);

        if (session.id === currentSessionId) li.classList.add('active');
        historyList.appendChild(li);
    });
}

async function startNewChat() {
    try {
        const res = await fetch('/sessions/new', {
            method: 'POST',
            headers: { 'X-User-ID': getUserId() }
        });
        const data = await res.json();
        currentSessionId = data.id;

        document.getElementById('messages-container').innerHTML = `
            <div class="message ai-message">
                <div class="avatar">AI</div>
                <div class="content">Hello! I'm OS Buddy. Ready for a new topic?</div>
            </div>
        `;

        // Refresh list instantly (New Chat appears in sidebar)
        fetchSessions();

        // Remove active class from others
        document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
    } catch (e) {
        console.error("Failed to create new chat", e);
    }
}

async function loadSession(sessionId) {
    currentSessionId = sessionId;
    // Fetch History
    try {
        const res = await fetch(`/sessions/${sessionId}`, {
            headers: { 'X-User-ID': getUserId() }
        });
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

async function deleteSession(sessionId) {
    if (!confirm("Delete this chat?")) return;

    try {
        await fetch(`/sessions/${sessionId}`, {
            method: 'DELETE',
            headers: { 'X-User-ID': getUserId() }
        });

        // If we deleted the active chat, reset view
        if (currentSessionId === sessionId) {
            currentSessionId = null;
            document.getElementById('messages-container').innerHTML = `
            <div class="message ai-message">
                <div class="avatar">AI</div>
                <div class="content">Chat deleted. Start a new one!</div>
            </div>
        `;
        }

        fetchSessions();
    } catch (e) {
        console.error("Delete failed", e);
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
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': getUserId()
            },
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
    // 0. Cleanup previous renderer hacks if any

    // 1. Extract Mermaid blocks
    const mermaidBlocks = [];
    const processedText = text.replace(/```mermaid\s*([\s\S]*?)\s*```/g, (match, code) => {
        mermaidBlocks.push(code);
        // Use a placeholder that is unlikely to be touched by marked.js
        // We use a custom ID structure we can find in the DOM later
        return `<span id="mermaid-placeholder-${mermaidBlocks.length - 1}" class="mermaid-marker"></span>`;
    });

    // 2. Parse Markdown
    let contentHtml = processedText;
    if (typeof marked !== 'undefined' && type === 'ai-message') {
        contentHtml = marked.parse(processedText);
    }

    // 3. Set HTML first
    msgDiv.innerHTML = `
        <div class="avatar">${type === 'user-message' ? 'U' : 'AI'}</div>
        <div class="content">${contentHtml}</div>
    `;

    // 4. Restore Mermaid blocks via DOM (Safer than string replacement)
    // This prevents browser from parsing mermaid chars like '<' or '&' as HTML
    const markers = msgDiv.querySelectorAll('.mermaid-marker');
    markers.forEach(marker => {
        const idParts = marker.id.split('-');
        const index = parseInt(idParts[idParts.length - 1]);
        let code = mermaidBlocks[index];

        // SAFETY: Decode HTML entities just in case (e.g. &gt; -> >)
        // and trim whitespace which can confuse mermaid
        const txt = document.createElement("textarea");
        txt.innerHTML = code;
        code = txt.value.trim();

        const div = document.createElement('div');
        div.classList.add('mermaid');
        div.textContent = code; // CRITICAL: textContent escapes special chars effectively for display

        // Replace the marker with the actual code div
        marker.replaceWith(div);
    });

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;

    // 5. Run Mermaid
    if (type === 'ai-message' && typeof mermaid !== 'undefined') {
        try {
            mermaid.run({
                nodes: msgDiv.querySelectorAll('.mermaid')
            });
        } catch (err) {
            console.error("Mermaid Render Error:", err);
            // Fallback: Show raw code if render fails
            msgDiv.querySelectorAll('.mermaid').forEach(el => {
                el.style.whiteSpace = 'pre-wrap';
                el.style.fontFamily = 'monospace';
                el.innerText = "Diagram Error. Raw Code:\n" + el.textContent;
            });
        }
    }

    return msgDiv.id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Initialize mermaid
if (typeof mermaid !== 'undefined') {
    mermaid.initialize({ startOnLoad: false, theme: 'dark' });
}
