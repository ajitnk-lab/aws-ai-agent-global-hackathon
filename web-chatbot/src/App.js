import React, { useState, useEffect } from 'react';
import { BedrockAgentRuntimeClient, InvokeAgentCommand } from '@aws-sdk/client-bedrock-agent-runtime';
import { CognitoIdentityProviderClient, InitiateAuthCommand } from '@aws-sdk/client-cognito-identity-provider';
import { fromCognitoIdentityPool } from '@aws-sdk/credential-providers';
import './App.css';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState(null);

  // AWS Configuration
  const AWS_CONFIG = {
    region: 'us-east-1',
    agentId: 'KS91Z9H2MA',
    agentAliasId: 'UEWYRHGIEL',
    identityPoolId: 'us-east-1:6feda4ed-660d-461c-8d68-90c9ce34a15a',
    userPoolId: 'us-east-1_W9Ro1YsQX',
    clientId: '613pomsjrqs8om564unnl6nutv'
  };

  // Auto-login with predefined credentials
  useEffect(() => {
    autoLogin();
  }, []);

  const autoLogin = async () => {
    try {
      const cognitoClient = new CognitoIdentityProviderClient({ region: AWS_CONFIG.region });
      
      const command = new InitiateAuthCommand({
        AuthFlow: 'USER_PASSWORD_AUTH',
        ClientId: AWS_CONFIG.clientId,
        AuthParameters: {
          USERNAME: 'chatbot-user',
          PASSWORD: 'ChatbotPass123!'
        }
      });

      const response = await cognitoClient.send(command);
      const token = response.AuthenticationResult.IdToken;
      
      setAuthToken(token);
      setIsAuthenticated(true);
      
      console.log('✅ Auto-login successful');
      
    } catch (error) {
      console.error('❌ Auto-login failed:', error);
      setMessages([{
        type: 'bot',
        content: 'Authentication failed. Please refresh the page to try again.'
      }]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !isAuthenticated) return;

    const userMessage = { type: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const bedrockClient = new BedrockAgentRuntimeClient({
        region: AWS_CONFIG.region,
        credentials: fromCognitoIdentityPool({
          clientConfig: { region: AWS_CONFIG.region },
          identityPoolId: AWS_CONFIG.identityPoolId,
          logins: {
            [`cognito-idp.${AWS_CONFIG.region}.amazonaws.com/${AWS_CONFIG.userPoolId}`]: authToken
          }
        }),
      });

      const command = new InvokeAgentCommand({
        agentId: AWS_CONFIG.agentId,
        agentAliasId: AWS_CONFIG.agentAliasId,
        sessionId: `session-${Date.now()}`,
        inputText: input,
      });

      const response = await bedrockClient.send(command);
      
      let responseText = '';
      for await (const event of response.completion) {
        if (event.chunk?.bytes) {
          responseText += new TextDecoder().decode(event.chunk.bytes);
        }
      }

      const botMessage = { type: 'bot', content: responseText };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { 
        type: 'bot', 
        content: `Error: ${error.message}` 
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const sampleQueries = [
    "Check security services configuration for us-east-1 region",
    "Get high severity security findings, limit to 3 results",
    "Analyze security posture with recommendations",
    "List 1 security hub finding from us-east-1 region of high risk"
  ];

  if (!isAuthenticated) {
    return (
      <div className="app">
        <header className="app-header">
          <h1>🛡️ AgentCore Security Assessment</h1>
          <p>Authenticating...</p>
        </header>
        <div className="chat-container">
          <div className="messages">
            <div className="message bot">
              <div className="message-content">
                🔐 Logging in automatically with predefined credentials...
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🛡️ AgentCore Security Assessment</h1>
        <p>AI-powered AWS security analysis with natural language queries</p>
        <small>✅ Authenticated as: chatbot-user</small>
      </header>

      <div className="chat-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome">
              <h3>Welcome! Try these sample queries:</h3>
              <div className="sample-queries">
                {sampleQueries.map((query, index) => (
                  <button
                    key={index}
                    className="sample-query"
                    onClick={() => setInput(query)}
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-content">
                {message.content}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="message bot">
              <div className="message-content loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                Analyzing security posture...
              </div>
            </div>
          )}
        </div>

        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your AWS security posture..."
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>

      <footer className="app-footer">
        <p>Powered by AWS Bedrock Agent & AgentCore | 
          <a href="https://github.com/ajitnk-lab/agentcore-security-assessment" target="_blank" rel="noopener noreferrer">
            View Source
          </a>
        </p>
      </footer>
    </div>
  );
};

export default App;
