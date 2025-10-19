"""
Working Lambda bridge: Bedrock Agent → AgentCore Gateway
"""
import json
import urllib3
import os
from datetime import datetime

def lambda_handler(event, context):
    """Lambda handler for Bedrock Agent requests"""
    
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract Bedrock Agent request details
        action_group = event.get('actionGroup', '')
        function_name = event.get('function', '')
        input_text = event.get('inputText', '')
        session_id = event.get('sessionId', '')
        parameters = {}
        
        # Parse parameters from Bedrock Agent
        if 'parameters' in event:
            for param in event['parameters']:
                param_name = param.get('name', '')
                param_value = param.get('value', '')
                if param_name:
                    parameters[param_name] = param_value
        
        print(f"Calling AgentCore Gateway: {function_name} with parameters: {parameters}")
        
        # Get environment variables
        gateway_url = os.environ.get('GATEWAY_URL')
        token_endpoint = os.environ.get('COGNITO_TOKEN_ENDPOINT')
        client_id = os.environ.get('COGNITO_CLIENT_ID')
        client_secret = os.environ.get('COGNITO_CLIENT_SECRET')
        cognito_scope = os.environ.get('COGNITO_SCOPE', 'openid')
        
        if not all([gateway_url, token_endpoint, client_id, client_secret]):
            raise Exception("Missing required environment variables")
        
        # Get Cognito token
        http = urllib3.PoolManager()
        
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': cognito_scope
        }
        
        token_response = http.request(
            'POST',
            token_endpoint,
            fields=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if token_response.status != 200:
            print(f"Token response status: {token_response.status}")
            print(f"Token response data: {token_response.data.decode()}")
            raise Exception(f"Failed to get access token: {token_response.status}")
        
        token_data = json.loads(token_response.data.decode())
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise Exception("No access token received")
        
        # Call AgentCore Gateway
        gateway_request = {
            'function': function_name,
            'parameters': parameters,
            'inputText': input_text,
            'sessionId': session_id,
            'actionGroup': action_group
        }
        
        gateway_response = http.request(
            'POST',
            gateway_url,
            body=json.dumps(gateway_request),
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        
        if gateway_response.status != 200:
            print(f"Gateway response status: {gateway_response.status}")
            print(f"Gateway response data: {gateway_response.data.decode()}")
            raise Exception(f"Gateway request failed: {gateway_response.status}")
        
        gateway_result = json.loads(gateway_response.data.decode())
        
        # Return in Bedrock Agent format
        response = {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'function': function_name,
                'functionResponse': {
                    'responseBody': {
                        'TEXT': {
                            'body': json.dumps(gateway_result, indent=2)
                        }
                    }
                }
            }
        }
        
        print(f"Returning response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        
        # Proper error response format
        error_response = {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', ''),
                'function': event.get('function', ''),
                'functionResponse': {
                    'responseBody': {
                        'TEXT': {
                            'body': json.dumps({
                                'error': str(e),
                                'message': 'Failed to process security assessment request',
                                'timestamp': datetime.now().isoformat()
                            }, indent=2)
                        }
                    }
                }
            }
        }
        
        return error_response
