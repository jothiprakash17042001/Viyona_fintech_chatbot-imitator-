console.log("Chatbot script loaded");
const messagesEl = document.getElementById("messages");
const userInputEl = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const chatbox = document.getElementById("chatbox");
const chatbotIcon = document.getElementById("chatbot-icon");
const closeChat = document.getElementById("close-chat");

let typingIndicator = null;
let isChatStarted = false; // Flag to prevent multiple initial messages

const emojiMap = {
    "payin": "💳",
    "payout": "📤",
    "virtual account": "🏦",
    "upi": "📱",
    "connecting banks": "🔗",
    "about us": "🤝",
    "careers": "💼",
    "schedule a demo": "📅",
    "i need a custom chatbot": "🤖",
    "partnership program": "🤝",
    "chat with me!": "💬",
    "case studies": "🔍",
    "back": "⬅️",
    "main menu": "🏠",
    "start over": "🔄"
};

function addMessage(text, isUser = false) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${isUser ? "user" : "bot"}`;

    if (!isUser) {
        const img = document.createElement("img");
        img.src = "/static/logo.png";
        img.alt = "Bot";
        wrapper.appendChild(img);
    }

    const span = document.createElement("span");
    span.textContent = text;
    wrapper.appendChild(span);

    messagesEl.appendChild(wrapper);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showTyping() {
    if (typingIndicator) return;
    typingIndicator = document.createElement("div");
    typingIndicator.className = "message bot typing";

    const img = document.createElement("img");
    img.src = "/static/logo.png";
    img.alt = "Bot";
    typingIndicator.appendChild(img);

    const dots = document.createElement("div");
    dots.className = "typing-dots";
    dots.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    typingIndicator.appendChild(dots);

    messagesEl.appendChild(typingIndicator);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
    if (!typingIndicator) return;
    typingIndicator.remove();
    typingIndicator = null;
}

function renderOptions(options = []) {
    if (options.length === 0) return;

    const container = document.createElement("div");
    container.className = "options-container";

    options.forEach(opt => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        
        const normalized = opt.trim().toLowerCase();
        const emoji = emojiMap[normalized] || "👉";
        
        btn.innerHTML = `<span class="option-icon">${emoji}</span> ${opt}`;

        const isNav = ["back", "main menu", "start over"].includes(normalized);

        btn.onclick = () => {
            // Optional: container.classList.add('fade-out'); // You could hide them after click
            sendMessage(opt, { showUser: !isNav, clear: isNav });
        };
        container.appendChild(btn);
    });

    messagesEl.appendChild(container);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setChatVisibility(visible) {
    chatbox.style.display = visible ? "flex" : "none";
}

async function sendMessage(message, { showUser = true, clear = false } = {}) {
    if (message === null || message === undefined) return;

    const normalized = String(message).trim().toLowerCase();
    const shouldClear = ["back", "main menu", "start over"].includes(normalized);

    if (shouldClear || clear) {
        messagesEl.innerHTML = "";
    }

    if (!shouldClear && normalized !== "" && showUser) {
        addMessage(message, true);
    }

    userInputEl.value = "";

    showTyping();
    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const data = await res.json();
        
        hideTyping();

        // Sequential delivery
        if (data.bot) {
            addMessage(data.bot);
            if (data.second_line || (data.options && data.options.length > 0)) {
                showTyping();
                await new Promise(r => setTimeout(r, 1200)); // Delay for natural feel
                hideTyping();
            }
        }

        if (data.second_line) {
            addMessage(data.second_line);
            if (data.options && data.options.length > 0) {
                showTyping();
                await new Promise(r => setTimeout(r, 800));
                hideTyping();
            }
        }

        if (data.options) {
            renderOptions(data.options);
        }

    } catch (err) {
        hideTyping();
        addMessage("Something went wrong...");
    }
}

sendBtn.addEventListener("click", () => sendMessage(userInputEl.value));
userInputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage(userInputEl.value);
});

closeChat.addEventListener("click", () => setChatVisibility(false));

// Auto-open is disabled as per user request. 
// The chatbot will only open when the logo is clicked.

function triggerInitialMessage() {
    if (isChatStarted) return;
    isChatStarted = true;
    showTyping();
    setTimeout(() => {
        sendMessage("");
    }, 1000);
}

// Keep the manual click as well
chatbotIcon.addEventListener("click", () => {
    setChatVisibility(true);
    if (!isChatStarted) {
        triggerInitialMessage();
    }
});
