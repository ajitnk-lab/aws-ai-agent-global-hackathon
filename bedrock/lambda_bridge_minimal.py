"""
Minimal Lambda bridge function: Bedrock Agent → Mock Security Data
"""
import json

def lambda_handler(event, context):
    """Lambda handler that returns mock security data"""
    
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
        
        # Route to mock functions based on function name
        if function_name == 'getSecurityFindings':
            result = get_mock_security_findings(parameters)
        elif function_name == 'checkSecurityServices':
            result = get_mock_security_services(parameters)
        elif function_name == 'analyzeSecurityPosture':
            result = get_mock_security_posture(parameters)
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

def get_mock_security_services(parameters):
    """Return mock security services configuration"""
    region = parameters.get('region', 'us-east-1')
    
    return {
        "region": region,
        "security_services": {
            "aws_security_hub": {
                "status": "ENABLED",
                "findings_count": 47,
                "compliance_score": 85
            },
            "aws_guardduty": {
                "status": "ENABLED", 
                "threat_intel_sets": 3,
                "malware_protection": "ENABLED"
            },
            "aws_config": {
                "status": "ENABLED",
                "rules_count": 23,
                "compliant_resources": 156,
                "non_compliant_resources": 8
            },
            "aws_cloudtrail": {
                "status": "ENABLED",
                "trails_count": 2,
                "data_events": "ENABLED"
            },
            "aws_inspector": {
                "status": "ENABLED",
                "assessments_count": 12,
                "findings_count": 34
            }
        },
        "recommendations": [
            "Enable AWS Security Hub in additional regions",
            "Configure GuardDuty malware protection for S3",
            "Review and remediate Config non-compliant resources",
            "Enable CloudTrail insights for anomaly detection"
        ]
    }

def get_mock_security_findings(parameters):
    """Return mock security findings"""
    severity = parameters.get('severity', 'HIGH')
    limit = int(parameters.get('limit', 10))
    
    all_findings = [
        {
            "id": "finding-001",
            "title": "S3 bucket allows public read access",
            "severity": "CRITICAL",
            "resource": "arn:aws:s3:::example-public-bucket",
            "region": "us-east-1",
            "remediation": "Remove public read access and use bucket policies"
        },
        {
            "id": "finding-002",
            "title": "EC2 security group allows unrestricted SSH",
            "severity": "HIGH", 
            "resource": "sg-0123456789abcdef0",
            "region": "us-east-1",
            "remediation": "Restrict SSH access to specific IP ranges"
        },
        {
            "id": "finding-003",
            "title": "RDS instance not encrypted",
            "severity": "HIGH",
            "resource": "arn:aws:rds:us-east-1:123456789012:db:mydb",
            "region": "us-east-1", 
            "remediation": "Enable encryption at rest for RDS instance"
        },
        {
            "id": "finding-004",
            "title": "IAM user with unused access keys",
            "severity": "MEDIUM",
            "resource": "arn:aws:iam::123456789012:user/old-user",
            "region": "global",
            "remediation": "Remove unused IAM access keys"
        },
        {
            "id": "finding-005",
            "title": "CloudTrail not enabled in region",
            "severity": "LOW",
            "resource": "arn:aws:cloudtrail:us-west-2:123456789012:trail/missing",
            "region": "us-west-2",
            "remediation": "Enable CloudTrail in all regions"
        }
    ]
    
    # Filter by severity if specified
    if severity and severity != 'ALL':
        filtered_findings = [f for f in all_findings if f['severity'] == severity]
    else:
        filtered_findings = all_findings
    
    # Apply limit
    limited_findings = filtered_findings[:limit]
    
    return {
        "findings": limited_findings,
        "total_count": len(filtered_findings),
        "severity_filter": severity,
        "limit": limit
    }

def get_mock_security_posture(parameters):
    """Return mock security posture analysis"""
    include_recommendations = parameters.get('include_recommendations', True)
    
    posture = {
        "overall_score": 78,
        "security_grade": "B+",
        "last_assessment": "2025-10-19T19:45:00Z",
        "categories": {
            "identity_and_access": {
                "score": 85,
                "status": "GOOD",
                "findings": 3
            },
            "data_protection": {
                "score": 72,
                "status": "NEEDS_IMPROVEMENT", 
                "findings": 8
            },
            "infrastructure_security": {
                "score": 80,
                "status": "GOOD",
                "findings": 5
            },
            "logging_and_monitoring": {
                "score": 75,
                "status": "GOOD",
                "findings": 4
            },
            "incident_response": {
                "score": 68,
                "status": "NEEDS_IMPROVEMENT",
                "findings": 6
            }
        }
    }
    
    if include_recommendations:
        posture["recommendations"] = [
            "Enable MFA for all IAM users",
            "Encrypt all S3 buckets with customer-managed keys",
            "Implement automated security scanning in CI/CD pipeline",
            "Set up centralized logging with CloudWatch",
            "Create incident response playbooks",
            "Enable AWS Config rules for compliance monitoring"
        ]
    
    return posture
