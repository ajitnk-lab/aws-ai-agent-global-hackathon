import React, { useState, useEffect } from 'react';
import { BedrockAgentRuntimeClient, InvokeAgentCommand } from '@aws-sdk/client-bedrock-agent-runtime';
import { CognitoIdentityProviderClient, InitiateAuthCommand } from '@aws-sdk/client-cognito-identity-provider';
import { STSClient, GetCallerIdentityCommand } from '@aws-sdk/client-sts';
import { fromCognitoIdentityPool } from '@aws-sdk/credential-providers';
import './App.css';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState(null);
  const [accountInfo, setAccountInfo] = useState(null);
  const [securityMetrics, setSecurityMetrics] = useState({
    postureScore: 'Click to load',
    criticalFindings: 'Click to load'
  });
  const [loadingStates, setLoadingStates] = useState({});
  const [showDashboard, setShowDashboard] = useState(true);

  // AWS Configuration
  const AWS_CONFIG = {
    region: 'us-east-1',
    agentId: 'KS91Z9H2MA',
    agentAliasId: 'UEWYRHGIEL',
    identityPoolId: 'us-east-1:6feda4ed-660d-461c-8d68-90c9ce34a15a',
    userPoolId: 'us-east-1_W9Ro1YsQX',
    clientId: '613pomsjrqs8om564unnl6nutv'
  };

  // Get specific security metrics on-demand
  const getSpecificMetrics = async (type) => {
    if (!authToken) return;
    
    setLoadingStates(prev => ({ ...prev, [type]: true }));
    
    try {
      const credentials = fromCognitoIdentityPool({
        clientConfig: { region: AWS_CONFIG.region },
        identityPoolId: AWS_CONFIG.identityPoolId,
        logins: {
          [`cognito-idp.${AWS_CONFIG.region}.amazonaws.com/${AWS_CONFIG.userPoolId}`]: authToken
        }
      });

      const bedrockClient = new BedrockAgentRuntimeClient({
        region: AWS_CONFIG.region,
        credentials: credentials,
      });

      const query = 'Get overall security posture score and critical findings count';

      const command = new InvokeAgentCommand({
        agentId: AWS_CONFIG.agentId,
        agentAliasId: AWS_CONFIG.agentAliasId,
        sessionId: `${type}-${Date.now()}`,
        inputText: query,
      });

      const response = await bedrockClient.send(command);
      
      let responseText = '';
      for await (const event of response.completion) {
        if (event.chunk?.bytes) {
          responseText += new TextDecoder().decode(event.chunk.bytes);
        }
      }

      console.log(`${type} Response:`, responseText);

      // Parse posture data
      const criticalMatch = responseText.match(/(\d+)\s*critical.*?findings?/i);
      const scoreMatch = responseText.match(/(?:overall\s+)?security\s+score\s+is\s+(\d+)/i) || responseText.match(/(?:Overall\s+)?Security\s+Posture\s+Score:\s*(\d+)/i);
      
      setSecurityMetrics(prev => ({
        ...prev,
        postureScore: scoreMatch ? `${scoreMatch[1]}%` : 'No data found',
        criticalFindings: criticalMatch ? criticalMatch[1] : 'No data found'
      }));

    } catch (error) {
      console.error(`${type} API Error:`, error);
      setSecurityMetrics(prev => ({
        ...prev,
        postureScore: 'Error - Check Console',
        criticalFindings: 'Error - Check Console'
      }));
    }
    
    setLoadingStates(prev => ({ ...prev, [type]: false }));
  };

  // Get AWS Account Information
  const getAccountInfo = async (credentials) => {
    try {
      const stsClient = new STSClient({ 
        region: AWS_CONFIG.region,
        credentials 
      });
      const command = new GetCallerIdentityCommand({});
      const response = await stsClient.send(command);
      setAccountInfo({
        accountId: response.Account,
        userId: response.UserId,
        arn: response.Arn
      });
    } catch (error) {
      console.error('Error getting account info:', error);
      // Set fallback account info if STS call fails
      setAccountInfo({
        accountId: 'Unable to retrieve',
        userId: 'N/A',
        arn: 'N/A'
      });
    }
  };

  // Auto-login with predefined credentials
  useEffect(() => {
    autoLogin();
  }, []);

  // Get security metrics after authentication
  useEffect(() => {
    // Remove automatic loading - now on-demand only
  }, [isAuthenticated, authToken]);

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
      
      // Get account information
      const credentials = fromCognitoIdentityPool({
        client: new CognitoIdentityProviderClient({ region: AWS_CONFIG.region }),
        identityPoolId: AWS_CONFIG.identityPoolId,
        logins: {
          [`cognito-idp.${AWS_CONFIG.region}.amazonaws.com/${AWS_CONFIG.userPoolId}`]: token
        }
      });
      
      await getAccountInfo(credentials);
      
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
    "Get HIGH severity security findings, limit to 3 results",
    "Get LOW severity security findings, limit to 3 results", 
    "Analyze security posture with recommendations"
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

      {/* Executive Dashboard */}
      {showDashboard && (
        <div className="dashboard">
          <div className="dashboard-header">
            <h2>📊 Executive Security Dashboard</h2>
            <button 
              className="toggle-dashboard" 
              onClick={() => setShowDashboard(false)}
            >
              ✕
            </button>
          </div>
          
          <div className="dashboard-grid">
            {/* Key Business Insights */}
            <div className="dashboard-card insights">
              <h3>🎯 Key Security Metrics</h3>
              <div className="insight-item">
                <span className="metric">{loadingStates.posture ? 'Loading...' : securityMetrics.postureScore}</span>
                <span className="label">Security Posture Score</span>
                <button onClick={() => getSpecificMetrics('posture')} disabled={loadingStates.posture}>
                  {loadingStates.posture ? 'Loading...' : 'Load Data'}
                </button>
              </div>
              <div className="insight-item">
                <span className="metric">{loadingStates.posture ? 'Loading...' : securityMetrics.criticalFindings}</span>
                <span className="label">Critical Findings</span>
              </div>
            </div>

            {/* System Information */}
            <div className="dashboard-card system-info">
              <h3>⚙️ System Configuration</h3>
              <div className="config-item">
                <span className="config-label">Agent ID:</span>
                <span className="config-value">{AWS_CONFIG.agentId}</span>
              </div>
              <div className="config-item">
                <span className="config-label">Session ID:</span>
                <span className="config-value">{Math.random().toString(36).substr(2, 9)}</span>
              </div>
              <div className="config-item">
                <span className="config-label">Region:</span>
                <span className="config-value">{AWS_CONFIG.region}</span>
              </div>
              <div className="config-item">
                <span className="config-label">Account ID:</span>
                <span className="config-value">{accountInfo?.accountId || 'Loading...'}</span>
              </div>
              <div className="config-item">
                <span className="config-label">Identity Pool:</span>
                <span className="config-value">{AWS_CONFIG.identityPoolId}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!showDashboard && (
        <button 
          className="show-dashboard" 
          onClick={() => setShowDashboard(true)}
        >
          📊 Show Executive Dashboard
        </button>
      )}

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
