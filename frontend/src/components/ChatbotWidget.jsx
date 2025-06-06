import React, { useState, useRef, useEffect } from 'react';
import './ChatbotWidget.css';

const LoadingDots = () => (
  <span className="chatbot-loading-dots">
    <span>.</span><span>.</span><span>.</span>
  </span>
);

// Helper to deduplicate consecutive messages (role+content)
function deduplicateHistory(history) {
  if (!Array.isArray(history)) return [];
  const deduped = [];
  for (const msg of history) {
    if (
      !deduped.length ||
      deduped[deduped.length - 1].role !== msg.role ||
      deduped[deduped.length - 1].content !== msg.content
    ) {
      deduped.push(msg);
    }
  }
  return deduped;
}

const ChatbotWidget = () => {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [chat, setChat] = useState([
    { role: 'assistant', content: 'Welcome to ERNET India! How can I help you?' }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (open && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chat, open]);

  const handleSend = async () => {
    if (!message.trim() || loading) return;
    setLoading(true);
    setError('');
    const userMsg = { role: 'user', content: message };
    setMessage('');
    try {
      const res = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          conversation_history: [...chat, userMsg]
        })
      });
      const data = await res.json();
      if (data.conversation_history) {
        setChat(deduplicateHistory(data.conversation_history));
      } else if (data.response) {
        setChat(c => deduplicateHistory([...c, { role: 'assistant', content: data.response }]));
      } else {
        setError('Sorry, no response.');
      }
    } catch (e) {
      setError('Sorry, there was an error connecting to the server.');
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !loading) handleSend();
  };

  return (
    <div className="chatbot-widget-fixed">
      {open ? (
        <div className="chatbot-widget-box chatbot-animate-in">
          <div className="chatbot-widget-header">
            <span className="chatbot-title">ERNET India</span>
            <button className="chatbot-widget-close" onClick={() => setOpen(false)} title="Close">×</button>
          </div>
          <div className="chatbot-widget-content">
            {chat.map((msg, idx) => (
              <div
                key={idx}
                className={`chatbot-msg chatbot-msg-${msg.role}`}
                style={{ animationDelay: `${idx * 0.04}s` }}
              >
                {msg.content}
              </div>
            ))}
            {loading && <div className="chatbot-msg chatbot-msg-assistant"><LoadingDots /></div>}
            {error && <div className="chatbot-msg chatbot-msg-error">{error}</div>}
            <div ref={chatEndRef} />
          </div>
          <div className="chatbot-widget-inputbar">
            <input
              className="chatbot-widget-input"
              type="text"
              placeholder="Type your message..."
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus={open}
              disabled={loading}
              maxLength={500}
            />
            <button
              className="chatbot-widget-submit"
              onClick={handleSend}
              disabled={!message.trim() || loading}
            >
              {loading ? <LoadingDots /> : 'Send'}
            </button>
          </div>
        </div>
      ) : (
        <button className="chatbot-widget-open chatbot-animate-in" onClick={() => setOpen(true)} title="Open chat">
          <span role="img" aria-label="chat">💬</span>
        </button>
      )}
    </div>
  );
};

export default ChatbotWidget; 