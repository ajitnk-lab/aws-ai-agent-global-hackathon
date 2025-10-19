"""
Lambda bridge function: Bedrock Agent → AgentCore Gateway (Built-in libraries only)
"""
import json
import urllib.request
import urllib.parse
import urllib.error
import os
from datetime import datetime

def lambda_handler(event, context):
    """Lambda handler for Bedrock Agent requests"""
    
    try:
        print(f"Received event: {json.dumps(event)}")
        
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
        
        # Mock security assessment results for demonstration
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
                    'All core security services are enabled',
                    'Consider enabling AWS Shield Advanced for DDoS protection',
                    'Review CloudTrail log retention settings'
                ]
            },
            'getSecurityFindings': {
                'status': 'success',
                'message': 'Security findings retrieved',
                'findings_count': 3,
                'severity_filter': parameters.get('severity', 'HIGH'),
                'limit': parameters.get('limit', 10),
                'findings': [
                    {
                        'id': 'finding-001',
                        'title': 'S3 bucket allows public read access',
                        'severity': 'HIGH',
                        'resource': 'arn:aws:s3:::example-public-bucket',
                        'description': 'S3 bucket has public read permissions enabled',
                        'remediation': 'Remove public read access and use bucket policies'
                    },
                    {
                        'id': 'finding-002', 
                        'title': 'EC2 security group allows unrestricted SSH',
                        'severity': 'HIGH',
                        'resource': 'sg-0123456789abcdef0',
                        'description': 'Security group allows SSH access from 0.0.0.0/0',
                        'remediation': 'Restrict SSH access to specific IP ranges'
                    },
                    {
                        'id': 'finding-003',
                        'title': 'IAM user has unused access keys',
                        'severity': 'MEDIUM',
                        'resource': 'arn:aws:iam::123456789012:user/unused-user',
                        'description': 'IAM user has access keys that have not been used in 90+ days',
                        'remediation': 'Remove unused access keys or rotate them'
                    }
                ]
            },
            'analyzeSecurityPosture': {
                'status': 'success',
                'message': 'Security posture analysis completed',
                'overall_score': 78,
                'score_breakdown': {
                    'identity_access': 85,
                    'data_protection': 72,
                    'infrastructure_security': 80,
                    'logging_monitoring': 75,
                    'incident_response': 70
                },
                'include_recommendations': parameters.get('include_recommendations', True),
                'recommendations': [
                    'Enable MFA for all IAM users and root account',
                    'Implement least privilege access policies',
                    'Enable encryption at rest for all S3 buckets',
                    'Set up automated security scanning with Inspector',
                    'Configure CloudWatch alarms for security events',
                    'Establish incident response procedures',
                    'Regular security training for development teams'
                ],
                'critical_issues': 2,
                'high_issues': 5,
                'medium_issues': 12,
                'low_issues': 8
            }
        }
        
        # Get mock response based on function name
        result = mock_responses.get(function, {
            'status': 'success',
            'message': f'Function {function} executed successfully',
            'parameters_received': parameters
        })
        
        # Format response for Bedrock Agent
        response_body = {
            'TEXT': {
                'body': json.dumps(result, indent=2)
            }
        }
        
        response = {
            'actionGroup': action_group,
            'function': function,
            'functionResponse': {
                'responseBody': response_body
            }
        }
        
        print(f"Returning response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        
        # Return error response to Bedrock Agent
        error_response = {
            'TEXT': {
                'body': json.dumps({
                    'error': str(e),
                    'message': 'Failed to process security assessment request',
                    'status': 'error'
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
