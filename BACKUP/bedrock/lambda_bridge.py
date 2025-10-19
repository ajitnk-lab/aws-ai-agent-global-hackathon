"""
Lambda bridge function: Bedrock Agent → AgentCore Gateway
"""
import json
import httpx
import asyncio
import os
from datetime import datetime, timedelta

# Gateway configuration (loaded from environment)
GATEWAY_URL = os.getenv('GATEWAY_URL')
COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
COGNITO_CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET')
COGNITO_TOKEN_ENDPOINT = os.getenv('COGNITO_TOKEN_ENDPOINT')
COGNITO_SCOPE = os.getenv('COGNITO_SCOPE')

# Token cache
_token_cache = {
    'token': None,
    'expires_at': None
}

async def get_oauth_token():
    """Get OAuth token from Cognito with caching"""
    global _token_cache
    
    # Check if cached token is still valid
    if (_token_cache['token'] and 
        _token_cache['expires_at'] and 
        _token_cache['expires_at'] > datetime.now()):
        return _token_cache['token']
    
    # Get new token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            COGNITO_TOKEN_ENDPOINT,
            data={
                'grant_type': 'client_credentials',
                'client_id': COGNITO_CLIENT_ID,
                'client_secret': COGNITO_CLIENT_SECRET,
                'scope': COGNITO_SCOPE
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code != 200:
            raise Exception(f"OAuth token request failed: {response.text}")
        
        token_data = response.json()
        _token_cache['token'] = token_data['access_token']
        
        # Cache token with 5-minute buffer
        expires_in = token_data.get('expires_in', 3600) - 300
        _token_cache['expires_at'] = datetime.now() + timedelta(seconds=expires_in)
        
        return _token_cache['token']

async def call_agentcore_gateway(tool_name: str, parameters: dict):
    """Call AgentCore Gateway tool via MCP protocol"""
    
    if not GATEWAY_URL:
        raise Exception("Gateway URL not configured")
    
    # Get OAuth token
    token = await get_oauth_token()
    
    # Map Bedrock Agent operations to AgentCore tools
    tool_mapping = {
        'checkSecurityServices': 'check_security_services',
        'getSecurityFindings': 'get_security_findings', 
        'analyzeSecurityPosture': 'analyze_security_posture',
        'exploreAwsResources': 'explore_aws_resources',
        'getComplianceStatus': 'get_resource_compliance_status'
    }
    
    agentcore_tool = tool_mapping.get(tool_name, tool_name)
    
    # Call Gateway using MCP protocol
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GATEWAY_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": agentcore_tool,
                    "arguments": parameters
                }
            },
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"Gateway request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if 'error' in result:
            raise Exception(f"Gateway tool error: {result['error']}")
        
        return result.get('result', {})

def lambda_handler(event, context):
    """Lambda handler for Bedrock Agent requests"""
    
    try:
        # Extract Bedrock Agent request details
        action_group = event.get('actionGroup', '')
        function = event.get('function', '')
        parameters = {}
        
        # Parse parameters from Bedrock Agent
        for param in event.get('parameters', []):
            param_name = param.get('name', '')
            param_value = param.get('value', '')
            if param_name:
                parameters[param_name] = param_value
        
        print(f"Processing request: {function} with parameters: {parameters}")
        
        # Call AgentCore Gateway
        result = asyncio.run(call_agentcore_gateway(function, parameters))
        
        # Format response for Bedrock Agent
        response_body = {
            'TEXT': {
                'body': json.dumps(result, indent=2)
            }
        }
        
        return {
            'actionGroup': action_group,
            'function': function,
            'functionResponse': {
                'responseBody': response_body
            }
        }
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        
        # Return error response to Bedrock Agent
        error_response = {
            'TEXT': {
                'body': json.dumps({
                    'error': str(e),
                    'message': 'Failed to process security assessment request'
                })
            }
        }
        
        return {
            'actionGroup': event.get('actionGroup', ''),
            'function': event.get('function', ''),
            'functionResponse': {
                'responseBody': error_response
            }
        }
