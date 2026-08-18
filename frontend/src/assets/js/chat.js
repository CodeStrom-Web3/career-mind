/* =========================================================
   chat.js — Career Assistant page
   Currently simulates the agent locally so the page is
   demoable without a backend. Replace `getAgentReply()`
   with a real call to services/api.js -> POST /agent/chat
   once the FastAPI + Bedrock endpoint exists.
   ========================================================= */

const chatLog = document.getElementById('chatLog');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');

function appendMessage(text, role) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
  return div;
}

function appendTyping() {
  const div = document.createElement('div');
  div.className = 'msg agent';
  div.innerHTML = '<span class="typing"><span></span><span></span><span></span></span>';
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
  return div;
}

function getAgentReply(userText) {
  const lower = userText.toLowerCase();
  if (lower.includes('next') || lower.includes('learn')) {
    return {
      text: "Given your Python, SQL and Power BI skills, I'd focus on statistics fundamentals next — it's the biggest gap for the Data Analyst roles you're targeting.",
      retrieved: 'goal, 3 active skills, 1 identified gap',
    };
  }
  if (lower.includes('project')) {
    return {
      text: 'Your Sales Dashboard project is a strong portfolio piece. Pairing it with a stats-heavy project next would round things out nicely.',
      retrieved: '1 stored project, goal',
    };
  }
  return {
    text: "Got it — I've noted that. I'll factor it in next time I suggest a roadmap step.",
    retrieved: 'conversation history updated',
  };
}

if (chatForm) {
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    chatInput.value = '';

    const typingEl = appendTyping();

    setTimeout(() => {
      typingEl.remove();
      const reply = getAgentReply(text);
      const el = appendMessage(reply.text, 'agent');
      const tag = document.createElement('span');
      tag.className = 'retrieved';
      tag.textContent = `↳ retrieved: ${reply.retrieved}`;
      el.appendChild(document.createElement('br'));
      el.appendChild(tag);
    }, 900);
  });
}