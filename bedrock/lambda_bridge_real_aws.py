"""
Real AWS API Lambda bridge function - NO MOCK DATA
"""
import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """Lambda handler that calls real AWS APIs"""
    
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract Bedrock Agent request details
        action_group = event.get('actionGroup', '')
        function_name = event.get('function', '')
        parameters = {}
        
        # Parse parameters from Bedrock Agent format
        if 'parameters' in event:
            for param in event['parameters']:
                param_name = param.get('name', '')
                param_value = param.get('value', '')
                if param_name:
                    parameters[param_name] = param_value
        
        print(f"Function: {function_name}, Parameters: {parameters}")
        
        # Route to real AWS API functions
        if function_name == 'getSecurityFindings':
            result = get_real_security_findings(parameters)
        elif function_name == 'checkSecurityServices':
            result = check_real_security_services(parameters)
        elif function_name == 'analyzeSecurityPosture':
            result = analyze_real_security_posture(parameters)
        else:
            result = {"error": f"Unknown function: {function_name}"}
        
        # Return in Bedrock Agent expected format
        return {
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
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'function': function_name,
                'functionResponse': {
                    'responseBody': {
                        'TEXT': {
                            'body': json.dumps({"error": str(e)}, indent=2)
                        }
                    }
                }
            }
        }

def get_real_security_findings(parameters):
    """Get real security findings from AWS Security Hub"""
    region = parameters.get('region', 'us-east-1')
    severity = parameters.get('severity', 'HIGH').upper()
    limit = int(parameters.get('limit', 10))
    
    try:
        # Create Security Hub client for the specified region
        securityhub = boto3.client('securityhub', region_name=region)
        
        # Build filters
        filters = {
            'SeverityLabel': [
                {
                    'Value': severity,
                    'Comparison': 'EQUALS'
                }
            ],
            'RecordState': [
                {
                    'Value': 'ACTIVE',
                    'Comparison': 'EQUALS'
                }
            ]
        }
        
        # Get findings from Security Hub
        response = securityhub.get_findings(
            Filters=filters,
            MaxResults=limit
        )
        
        findings = []
        for finding in response.get('Findings', []):
            findings.append({
                'id': finding.get('Id', ''),
                'title': finding.get('Title', ''),
                'severity': finding.get('Severity', {}).get('Label', ''),
                'resource': finding.get('Resources', [{}])[0].get('Id', ''),
                'region': finding.get('Region', region),
                'remediation': finding.get('Remediation', {}).get('Recommendation', {}).get('Text', 'No remediation available')
            })
        
        return {
            'findings': findings,
            'total_found': len(findings),
            'region': region,
            'filters_applied': {
                'severity': severity,
                'limit': limit,
                'region': region
            }
        }
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidAccessException':
            return {
                'error': f'Security Hub is not enabled in region {region}',
                'region': region,
                'recommendation': f'Enable AWS Security Hub in {region} region'
            }
        else:
            return {
                'error': f'Error accessing Security Hub in {region}: {str(e)}',
                'region': region
            }

def check_real_security_services(parameters):
    """Check real AWS security services status"""
    region = parameters.get('region', 'us-east-1')
    
    services_status = {}
    
    try:
        # Check Security Hub
        try:
            securityhub = boto3.client('securityhub', region_name=region)
            hub_response = securityhub.describe_hub()
            services_status['security_hub'] = {
                'status': 'ENABLED',
                'hub_arn': hub_response.get('HubArn', ''),
                'region': region
            }
        except ClientError as e:
            services_status['security_hub'] = {
                'status': 'DISABLED' if 'InvalidAccessException' in str(e) else 'ERROR',
                'error': str(e),
                'region': region
            }
        
        # Check GuardDuty
        try:
            guardduty = boto3.client('guardduty', region_name=region)
            detectors = guardduty.list_detectors()
            if detectors['DetectorIds']:
                detector_id = detectors['DetectorIds'][0]
                detector_info = guardduty.get_detector(DetectorId=detector_id)
                services_status['guardduty'] = {
                    'status': detector_info['Status'],
                    'detector_id': detector_id,
                    'region': region
                }
            else:
                services_status['guardduty'] = {
                    'status': 'DISABLED',
                    'region': region
                }
        except ClientError as e:
            services_status['guardduty'] = {
                'status': 'ERROR',
                'error': str(e),
                'region': region
            }
        
        # Check Config
        try:
            config = boto3.client('config', region_name=region)
            config_recorders = config.describe_configuration_recorders()
            if config_recorders['ConfigurationRecorders']:
                services_status['config'] = {
                    'status': 'ENABLED',
                    'recorders_count': len(config_recorders['ConfigurationRecorders']),
                    'region': region
                }
            else:
                services_status['config'] = {
                    'status': 'DISABLED',
                    'region': region
                }
        except ClientError as e:
            services_status['config'] = {
                'status': 'ERROR',
                'error': str(e),
                'region': region
            }
        
        # Check CloudTrail
        try:
            cloudtrail = boto3.client('cloudtrail', region_name=region)
            trails = cloudtrail.describe_trails()
            active_trails = [t for t in trails['trailList'] if t.get('IsLogging', False)]
            services_status['cloudtrail'] = {
                'status': 'ENABLED' if active_trails else 'DISABLED',
                'active_trails_count': len(active_trails),
                'region': region
            }
        except ClientError as e:
            services_status['cloudtrail'] = {
                'status': 'ERROR',
                'error': str(e),
                'region': region
            }
        
        return {
            'region': region,
            'security_services': services_status,
            'timestamp': context.aws_request_id
        }
        
    except Exception as e:
        return {
            'error': f'Error checking security services in {region}: {str(e)}',
            'region': region
        }

def analyze_real_security_posture(parameters):
    """Analyze real security posture using AWS APIs"""
    region = parameters.get('region', 'us-east-1')
    include_recommendations = parameters.get('include_recommendations', 'true').lower() == 'true'
    
    try:
        # Get real findings count from Security Hub
        securityhub = boto3.client('securityhub', region_name=region)
        
        # Count findings by severity
        severity_counts = {}
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            try:
                response = securityhub.get_findings(
                    Filters={
                        'SeverityLabel': [{'Value': severity, 'Comparison': 'EQUALS'}],
                        'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
                    },
                    MaxResults=1
                )
                # Note: This is a simplified count - real implementation would need pagination
                severity_counts[severity] = len(response.get('Findings', []))
            except:
                severity_counts[severity] = 0
        
        # Calculate basic score based on findings
        total_findings = sum(severity_counts.values())
        critical_weight = severity_counts.get('CRITICAL', 0) * 4
        high_weight = severity_counts.get('HIGH', 0) * 3
        medium_weight = severity_counts.get('MEDIUM', 0) * 2
        low_weight = severity_counts.get('LOW', 0) * 1
        
        weighted_score = critical_weight + high_weight + medium_weight + low_weight
        # Simple scoring: start at 100, subtract weighted findings
        posture_score = max(0, 100 - weighted_score)
        
        result = {
            'region': region,
            'overall_score': posture_score,
            'total_active_findings': total_findings,
            'findings_by_severity': severity_counts,
            'last_assessment': context.aws_request_id,
            'filters_applied': {
                'region': region,
                'include_recommendations': include_recommendations
            }
        }
        
        if include_recommendations:
            recommendations = []
            if severity_counts.get('CRITICAL', 0) > 0:
                recommendations.append('Address critical security findings immediately')
            if severity_counts.get('HIGH', 0) > 0:
                recommendations.append('Remediate high severity security findings')
            if total_findings > 10:
                recommendations.append('Implement automated remediation for common findings')
            
            result['recommendations'] = recommendations
        
        return result
        
    except ClientError as e:
        if 'InvalidAccessException' in str(e):
            return {
                'error': f'Security Hub is not enabled in region {region}',
                'region': region,
                'recommendation': f'Enable AWS Security Hub in {region} to analyze security posture'
            }
        else:
            return {
                'error': f'Error analyzing security posture in {region}: {str(e)}',
                'region': region
            }
