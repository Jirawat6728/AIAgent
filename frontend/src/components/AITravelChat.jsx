import React, { useState, useRef, useEffect } from 'react';
import './AITravelChat.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function AITravelChat({ user, onLogout }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: "Hi I'm your AI travel assistance. How can I help you with your travel plans today? I can help you find flights, search for hotels, or provide destination information!"
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check API connection
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/`);
      const data = await response.json();
      setIsConnected(data.message === "AI Travel Agent API is running");
    } catch (error) {
      console.error('API connection error:', error);
      setIsConnected(false);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;

    if (!isConnected) {
      alert('Backend is not connected. Please start the backend server first.');
      return;
    }

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: inputText
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputText;
    setInputText('');
    setIsTyping(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentInput,
          conversation_history: messages.map(m => ({
            role: m.type === 'user' ? 'user' : 'assistant',
            content: m.text
          }))
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      
      // Add AI text response
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: data.response,
        searchResults: data.search_results
      };
      
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error calling API:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: `❌ Error: ${error.message}\n\nPlease check:\n1. Backend is running\n2. API Keys are correct`
      };
      
      setMessages(prev => [...prev, errorMessage]);
      setIsConnected(false);
    } finally {
      setIsTyping(false);
    }
  };

  const getFollowUpMessage = (intentType) => {
    switch(intentType) {
      case 'flight':
        return "I can help you search for flights! Please provide:\n- Origin city (e.g., BKK for Bangkok)\n- Destination city (e.g., NRT for Tokyo)\n- Departure date (YYYY-MM-DD)\n- Return date (optional)\n- Number of adults";
      case 'hotel':
        return "I can help you find hotels! Please provide:\n- City code (e.g., NYC for New York)\n- Check-in date (YYYY-MM-DD)\n- Check-out date (YYYY-MM-DD)\n- Number of guests";
      default:
        return "How else can I assist you with your travel plans?";
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceInput = () => {
    if (!isRecording) {
      setIsRecording(true);
      
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          setInputText(transcript);
          setIsRecording(false);
        };

        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          setIsRecording(false);
          alert('Cannot use microphone. Please check microphone permissions.');
        };

        recognition.onend = () => {
          setIsRecording(false);
        };

        recognition.start();
      } else {
        alert('Your browser does not support speech recognition');
        setIsRecording(false);
      }
    } else {
      setIsRecording(false);
    }
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <header className="chat-page-header">
        <div className="chat-header-content">
          <div className="chat-logo-section">
            <div className="chat-logo-icon">
              <svg className="chat-plane-icon" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
              </svg>
            </div>
            <span className="chat-logo-text">AI Travel Agent</span>
          </div>
          <nav className="chat-nav-links">
            <a href="#" className="chat-nav-link">Flights</a>
            <a href="#" className="chat-nav-link">Hotels</a>
            <a href="#" className="chat-nav-link">Car Rentals</a>
            <a href="#" className="chat-nav-link">My Bookings</a>
          </nav>
          <div className="user-section">
            {user && (
              <div className="user-info">
                <div className="user-avatar">
                  <span className="user-initial">{user.name?.[0]?.toUpperCase()}</span>
                </div>
                <span className="user-name">{user.name}</span>
              </div>
            )}
            <button onClick={onLogout} className="btn-logout">
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <main className="chat-main">
        <div className="chat-box">
          
          {/* Chat Header */}
          <div className="chatbox-header">
            <div className="chatbox-header-left">
              <div className="chatbox-avatar">
                <svg className="chatbox-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h3 className="chatbox-title">AI Travel Assistant</h3>
                <div className="connection-status">
                  <div className={`status-dot ${isConnected ? 'status-connected' : 'status-disconnected'}`}></div>
                  <span className="status-text">
                    {isConnected ? 'Connected to FastAPI + Gemini + Amadeus' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Messages Area */}
          <div className="messages-area">
            <div className="messages-list">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`message-wrapper ${message.type === 'user' ? 'message-right' : 'message-left'}`}
                >
                  <div className={`message-bubble ${message.type === 'user' ? 'message-user' : 'message-bot'}`}>
                    <p className="message-text">{message.text}</p>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="typing-indicator">
                  <div className="typing-bubble">
                    <div className="typing-dots">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="input-area">
            <div className="input-wrapper">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about flights, hotels, or destinations..."
                rows="1"
                className="input-field"
              />
              <button
                onClick={handleVoiceInput}
                className={`btn-mic ${isRecording ? 'btn-mic-recording' : ''}`}
                title={isRecording ? 'Recording...' : 'Voice input'}
              >
                <svg className="mic-icon" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
              </button>
              <button
                onClick={handleSend}
                disabled={!inputText.trim()}
                className="btn-send"
              >
                Send
              </button>
            </div>
            {isRecording && (
              <div className="recording-status">
                🎤 Listening...
              </div>
            )}
            <div className="powered-by">
              Powered by Google Gemini AI + Amadeus API
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}