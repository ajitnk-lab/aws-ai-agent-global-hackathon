"""
Lambda bridge function: Fixed to use function name instead of action group name
"""
import json
import os
import requests
import base64

def lambda_handler(event, context):
    """Lambda handler with corrected function name mapping"""
    
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract function name from event (NOT action group name)
        function_name = event.get('function', '')
        parameters = []
        
        # Parse parameters from Bedrock Agent
        if 'parameters' in event:
            for param in event['parameters']:
                param_name = param.get('name', '')
                param_value = param.get('value', '')
                if param_name:
                    parameters.append({
                        'name': param_name,
                        'value': param_value
                    })
        
        print(f"Function: {function_name}")
        print(f"Bedrock Parameters: {parameters}")
        
        # Get OAuth token
        token = get_oauth_token()
        if not token:
            return create_error_response("Failed to obtain OAuth token")
        
        print("✅ OAuth token obtained successfully")
        
        # Map function name to tool name and parameters
        tool_name, mapped_params = map_parameters(function_name, parameters)
        
        # Call AgentCore Gateway
        gateway_url = os.environ['GATEWAY_URL']
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'tool_name': tool_name,
            'parameters': mapped_params
        }
        
        print(f"Calling gateway with: {payload}")
        
        response = requests.post(gateway_url, json=payload, headers=headers, timeout=25)
        
        if response.status_code == 200:
            result = response.json()
            return create_success_response(function_name, result)
        else:
            print(f"Gateway error: {response.status_code} - {response.text}")
            return create_error_response(f"Gateway error: {response.status_code}")
            
    except Exception as e:
        print(f"Exception: Lambda error: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_error_response(str(e))

def map_parameters(function_name, parameters):
    """Map Bedrock function names to AgentCore tool names and parameters"""
    
    # Convert parameters list to dict
    param_dict = {}
    for param in parameters:
        param_dict[param['name']] = param['value']
    
    # Map function names to tool names
    function_mapping = {
        'checkSecurityServices': 'check_security_services',
        'getSecurityFindings': 'get_security_findings', 
        'analyzeSecurityPosture': 'analyze_security_posture'
    }
    
    if function_name not in function_mapping:
        raise ValueError(f"Unknown function: {function_name}")
    
    tool_name = function_mapping[function_name]
    
    # Map parameters based on function
    if function_name == 'checkSecurityServices':
        mapped_params = {
            'region': param_dict.get('region', 'us-east-1')
        }
    elif function_name == 'getSecurityFindings':
        mapped_params = {
            'severity': param_dict.get('severity', 'HIGH'),
            'limit': int(param_dict.get('limit', 10))
        }
    elif function_name == 'analyzeSecurityPosture':
        mapped_params = {
            'include_recommendations': param_dict.get('include_recommendations', 'true').lower() == 'true'
        }
    else:
        mapped_params = param_dict
    
    return tool_name, mapped_params

def get_oauth_token():
    """Get OAuth token from Cognito"""
    try:
        token_url = os.environ['TOKEN_URL']
        client_id = os.environ['COGNITO_CLIENT_ID']
        client_secret = os.environ['COGNITO_CLIENT_SECRET']
        
        # Create basic auth header
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'agentcore/invoke'
        }
        
        response = requests.post(token_url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            print(f"Token obtained successfully (expires in {expires_in}s)")
            return access_token
        else:
            print(f"Token request failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Token error: {str(e)}")
        return None

def create_success_response(function_name, result):
    """Create successful Bedrock Agent response"""
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': 'security-tools',
            'function': function_name,
            'functionResponse': {
                'responseBody': {
                    'TEXT': {
                        'body': json.dumps(result, indent=2)
                    }
                }
            }
        }
    }

def create_error_response(error_message):
    """Create error response for Bedrock Agent"""
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': 'security-tools', 
            'function': 'error',
            'functionResponse': {
                'responseBody': {
                    'TEXT': {
                        'body': f"Error: {error_message}"
                    }
                }
            }
        }
    }
