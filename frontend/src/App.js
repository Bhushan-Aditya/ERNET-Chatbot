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
    <Container maxWidth="md" sx={{ height: '100vh', py: 4 }}>
      <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
          <Typography variant="h5" component="h1">
            ERNET Domain Registry Chatbot
          </Typography>
        </Box>

        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          <List>
            {conversation.map((msg, index) => (
              <ListItem
                key={index}
                sx={{
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    bgcolor: msg.role === 'user' ? 'primary.light' : 'grey.100',
                    color: msg.role === 'user' ? 'white' : 'text.primary',
                  }}
                >
                  <ListItemText primary={msg.content} />
                </Paper>
              </ListItem>
            ))}
            {loading && (
              <ListItem sx={{ justifyContent: 'flex-start' }}>
                <CircularProgress size={20} />
              </ListItem>
            )}
          </List>
        </Box>

        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <Button
              variant="contained"
              color="primary"
              endIcon={<SendIcon />}
              onClick={handleSend}
              disabled={loading || !message.trim()}
            >
              Send
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}

export default App; 