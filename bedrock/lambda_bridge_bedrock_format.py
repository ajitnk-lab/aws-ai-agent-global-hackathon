"""
Lambda bridge function: Proper Bedrock Agent response format
"""
import json
import os

def lambda_handler(event, context):
    """Lambda handler with proper Bedrock Agent response format"""
    
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract Bedrock Agent request details
        action_group = event.get('actionGroup', '')
        function_name = event.get('function', '')
        parameters = {}
        
        # Parse parameters from Bedrock Agent (Fix 3: Parameter format)
        if 'parameters' in event:
            for param in event['parameters']:
                param_name = param.get('name', '')
                param_value = param.get('value', '')
                if param_name:
                    parameters[param_name] = param_value
        
        # Also handle direct parameter object
        if 'requestBody' in event:
            if 'content' in event['requestBody']:
                if 'application/json' in event['requestBody']['content']:
                    body_params = event['requestBody']['content']['application/json']
                    if isinstance(body_params, dict):
                        parameters.update(body_params)
        
        print(f"Processing function: {function_name} with parameters: {parameters}")
        
        # Mock security assessment results with parameter handling
        mock_responses = {
            'checkSecurityServices': {
                'status': 'success',
                'message': 'Security services check completed',
                'services': {
                    'SecurityHub': 'enabled',
                    'GuardDuty': 'enabled', 
                    'Config': 'enabled',
                    'CloudTrail': 'enabled',
                    'Inspector': 'enabled'
                },
                'region': parameters.get('region', 'us-east-1'),
                'recommendations': [
                    f'Security services checked for region: {parameters.get("region", "us-east-1")}',
                    'All core security services are enabled',
                    'Consider enabling AWS Shield Advanced for DDoS protection'
                ]
            },
            'getSecurityFindings': {
                'status': 'success',
                'message': 'Security findings retrieved',
                'findings_count': 3,
                'severity_filter': parameters.get('severity', 'HIGH'),
                'limit': int(parameters.get('limit', 10)),
                'region': parameters.get('region', 'us-east-1'),
                'findings': [
                    {
                        'id': 'finding-001',
                        'title': 'S3 bucket allows public read access',
                        'severity': parameters.get('severity', 'HIGH'),
                        'resource': 'arn:aws:s3:::example-public-bucket',
                        'region': parameters.get('region', 'us-east-1'),
                        'remediation': 'Remove public read access and use bucket policies'
                    },
                    {
                        'id': 'finding-002', 
                        'title': 'EC2 security group allows unrestricted SSH',
                        'severity': parameters.get('severity', 'HIGH'),
                        'resource': 'sg-0123456789abcdef0',
                        'region': parameters.get('region', 'us-east-1'),
                        'remediation': 'Restrict SSH access to specific IP ranges'
                    }
                ][:int(parameters.get('limit', 10))]
            },
            'analyzeSecurityPosture': {
                'status': 'success',
                'message': 'Security posture analysis completed',
                'overall_score': 78,
                'service_focus': parameters.get('service', 'All services'),
                'include_recommendations': parameters.get('include_recommendations', True),
                'score_breakdown': {
                    'identity_access': 85,
                    'data_protection': 72,
                    'infrastructure_security': 80,
                    'logging_monitoring': 75,
                    'incident_response': 70
                },
                'recommendations': [
                    f'Analysis focused on: {parameters.get("service", "All AWS services")}',
                    'Enable MFA for all IAM users and root account',
                    'Implement least privilege access policies',
                    'Enable encryption at rest for all S3 buckets',
                    'Set up automated security scanning with Inspector'
                ] if parameters.get('include_recommendations', True) else []
            }
        }
        
        # Get response based on function name
        result = mock_responses.get(function_name, {
            'status': 'success',
            'message': f'Function {function_name} executed successfully',
            'parameters_received': parameters
        })
        
        # Proper Bedrock Agent response format (Fix 2)
        response = {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
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
        
        print(f"Returning response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        
        # Proper error response format (Fix 4)
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
                                'status': 'error'
                            })
                        }
                    }
                }
            }
        }
        
        return error_response
