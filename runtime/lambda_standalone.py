"""
Standalone Lambda function that provides MCP tools directly without calling AgentCore Gateway
This should be deployed as SecurityMCPToolsLambda to act as the AgentCore Runtime
"""
import json
from datetime import datetime
from security_functions import get_security_findings, check_security_services, analyze_security_posture

def lambda_handler(event, context):
    """Lambda handler that provides MCP tools directly"""
    
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract function name and parameters
        function_name = event.get('function', '')
        action_group = event.get('actionGroup', '')
        
        # Parse parameters from Bedrock Agent
        parameters = {}
        if 'parameters' in event:
            for param in event['parameters']:
                param_name = param.get('name', '')
                param_value = param.get('value', '')
                if param_name:
                    parameters[param_name] = param_value
        
        print(f"Calling function: {function_name} with parameters: {parameters}")
        
        # Route to appropriate security function
        result = None
        
        if function_name == 'getSecurityFindings':
            result = get_security_findings(
                severity_filter=parameters.get('severity_filter'),
                limit=int(parameters.get('limit', 50)),
                region=parameters.get('region'),
                service_filter=parameters.get('service_filter'),
                resource_type=parameters.get('resource_type'),
                compliance_status=parameters.get('compliance_status')
            )
        elif function_name == 'checkSecurityServices':
            result = check_security_services()
        elif function_name == 'analyzeSecurityPosture':
            result = analyze_security_posture()
        else:
            result = json.dumps({
                'error': f'Unknown function: {function_name}',
                'available_functions': ['getSecurityFindings', 'checkSecurityServices', 'analyzeSecurityPosture']
            }, indent=2)
        
        # Return in Bedrock Agent format
        response = {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'function': function_name,
                'functionResponse': {
                    'responseBody': {
                        'TEXT': {
                            'body': result
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
