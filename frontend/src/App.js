import React, { useState } from 'react';
import {
  Container,
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';
import './index.css';
// Import new components (to be created)
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import SupportInfo from './components/SupportInfo';
import ChatbotWidget from './components/ChatbotWidget';

function App() {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!message.trim()) return;

    const userMessage = message;
    setMessage('');
    setLoading(true);

    // Add user message to conversation
    setConversation(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/chat', {
        message: userMessage,
        conversation_history: conversation,
      });

      // Add assistant response to conversation
      setConversation(response.data.conversation_history);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message to conversation
      setConversation(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, there was an error processing your request.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="ernet-app">
      <Header />
      <main className="ernet-main">
        <div className="ernet-floating-domains">
          <span className="ernet-floating-domain ernet-floating-domain-1">विद्या.भारत</span>
          <span className="ernet-floating-domain ernet-floating-domain-2">ac.in</span>
          <span className="ernet-floating-domain ernet-floating-domain-3">edu.in</span>
          <span className="ernet-floating-domain ernet-floating-domain-4">res.in</span>
          <span className="ernet-floating-domain ernet-floating-domain-5">शोध.भारत</span>
          <span style={{position:'relative',zIndex:2,fontWeight:700,fontSize:'2.2rem'}}>res.in <span style={{fontWeight:400}}>|</span> edu.in <span style={{fontWeight:400}}>|</span> ac.in</span>
        </div>
        <SearchBar />
        <SupportInfo />
      </main>
      <ChatbotWidget />
    </div>
  );
}

export default App; 