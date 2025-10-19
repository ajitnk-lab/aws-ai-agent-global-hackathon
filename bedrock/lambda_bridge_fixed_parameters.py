"""
Lambda bridge function: Fixed parameter handling for severity and limit
"""
import json
import os

def lambda_handler(event, context):
    """Lambda handler with proper parameter filtering"""
    
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract Bedrock Agent request details
        action_group = event.get('actionGroup', '')
        function_name = event.get('function', '')
        parameters = {}
        
        # Parse parameters from Bedrock Agent
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
        
        # Define all available findings with different severities
        all_findings = [
            {
                'id': 'finding-001',
                'title': 'S3 bucket allows public read access',
                'severity': 'CRITICAL',
                'resource': 'arn:aws:s3:::example-public-bucket',
                'region': 'us-east-1',
                'remediation': 'Remove public read access and use bucket policies'
            },
            {
                'id': 'finding-002', 
                'title': 'EC2 security group allows unrestricted SSH',
                'severity': 'HIGH',
                'resource': 'sg-0123456789abcdef0',
                'region': 'us-east-1',
                'remediation': 'Restrict SSH access to specific IP ranges'
            },
            {
                'id': 'finding-003',
                'title': 'RDS instance not encrypted',
                'severity': 'HIGH',
                'resource': 'arn:aws:rds:us-east-1:123456789012:db:mydb',
                'region': 'us-east-1',
                'remediation': 'Enable encryption at rest for RDS instance'
            },
            {
                'id': 'finding-004',
                'title': 'IAM user with unused access keys',
                'severity': 'MEDIUM',
                'resource': 'arn:aws:iam::123456789012:user/old-user',
                'region': 'global',
                'remediation': 'Remove unused IAM access keys'
            },
            {
                'id': 'finding-005',
                'title': 'CloudTrail logging not enabled',
                'severity': 'MEDIUM',
                'resource': 'arn:aws:cloudtrail:us-east-1:123456789012:trail/mytrail',
                'region': 'us-east-1',
                'remediation': 'Enable CloudTrail logging for audit purposes'
            },
            {
                'id': 'finding-006',
                'title': 'S3 bucket versioning not enabled',
                'severity': 'LOW',
                'resource': 'arn:aws:s3:::example-bucket-no-versioning',
                'region': 'us-east-1',
                'remediation': 'Enable S3 bucket versioning for data protection'
            },
            {
                'id': 'finding-007',
                'title': 'EC2 instance missing tags',
                'severity': 'LOW',
                'resource': 'i-0123456789abcdef0',
                'region': 'us-east-1',
                'remediation': 'Add proper tags for resource management'
            },
            {
                'id': 'finding-008',
                'title': 'Lambda function timeout too high',
                'severity': 'LOW',
                'resource': 'arn:aws:lambda:us-east-1:123456789012:function:myfunction',
                'region': 'us-east-1',
                'remediation': 'Optimize Lambda function timeout settings'
            }
        ]
        
        # Process different functions
        if function_name == 'getSecurityFindings':
            # Extract and validate parameters
            severity_filter = parameters.get('severity', '').upper()
            limit = int(parameters.get('limit', 10)) if parameters.get('limit') else 10
            
            print(f"Filtering by severity: {severity_filter}, limit: {limit}")
            
            # Filter findings by severity if specified
            filtered_findings = all_findings
            if severity_filter and severity_filter in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                filtered_findings = [f for f in all_findings if f['severity'] == severity_filter]
                print(f"Found {len(filtered_findings)} findings with severity {severity_filter}")
            
            # Apply limit
            limited_findings = filtered_findings[:limit]
            
            result = {
                'status': 'success',
                'message': f'Security findings retrieved with severity filter: {severity_filter or "ALL"}',
                'findings_count': len(limited_findings),
                'total_available': len(filtered_findings),
                'severity_filter': severity_filter or 'ALL',
                'limit_applied': limit,
                'findings': limited_findings
            }
            
        elif function_name == 'checkSecurityServices':
            region = parameters.get('region', 'us-east-1')
            result = {
                'status': 'success',
                'message': f'Security services check completed for region: {region}',
                'services': {
                    'SecurityHub': 'enabled',
                    'GuardDuty': 'enabled', 
                    'Config': 'enabled',
                    'CloudTrail': 'enabled',
                    'Inspector': 'enabled'
                },
                'region': region,
                'recommendations': [
                    f'Security services checked for region: {region}',
                    'All core security services are enabled',
                    'Consider enabling AWS Shield Advanced for DDoS protection'
                ]
            }
            
        elif function_name == 'analyzeSecurityPosture':
            include_recommendations = parameters.get('include_recommendations', True)
            if isinstance(include_recommendations, str):
                include_recommendations = include_recommendations.lower() == 'true'
                
            result = {
                'status': 'success',
                'message': 'Security posture analysis completed',
                'overall_score': 78,
                'critical_findings': len([f for f in all_findings if f['severity'] == 'CRITICAL']),
                'high_findings': len([f for f in all_findings if f['severity'] == 'HIGH']),
                'medium_findings': len([f for f in all_findings if f['severity'] == 'MEDIUM']),
                'low_findings': len([f for f in all_findings if f['severity'] == 'LOW']),
                'include_recommendations': include_recommendations,
                'score_breakdown': {
                    'identity_access': 85,
                    'data_protection': 72,
                    'infrastructure_security': 80,
                    'logging_monitoring': 75,
                    'incident_response': 70
                },
                'recommendations': [
                    'Enable MFA for all IAM users and root account',
                    'Implement least privilege access policies',
                    'Enable encryption at rest for all S3 buckets',
                    'Set up automated security scanning with Inspector'
                ] if include_recommendations else []
            }
            
        else:
            result = {
                'status': 'success',
                'message': f'Function {function_name} executed successfully',
                'parameters_received': parameters
            }
        
        # Proper Bedrock Agent response format
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
                                'status': 'error'
                            })
                        }
                    }
                }
            }
        }
        
        return error_response
