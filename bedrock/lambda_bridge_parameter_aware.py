"""
Parameter-aware Lambda bridge function: Properly filters by severity, limit, service, etc.
"""
import json

def lambda_handler(event, context):
    """Lambda handler that properly processes parameters"""
    
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
        
        # Route to functions with proper parameter handling
        if function_name == 'getSecurityFindings':
            result = get_security_findings_filtered(parameters)
        elif function_name == 'checkSecurityServices':
            result = get_security_services_filtered(parameters)
        elif function_name == 'analyzeSecurityPosture':
            result = get_security_posture_filtered(parameters)
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

def get_security_findings_filtered(parameters):
    """Return filtered security findings based on parameters"""
    severity = parameters.get('severity', 'ALL').upper()
    limit = int(parameters.get('limit', 10))
    service_filter = parameters.get('service_filter', '').lower()
    region = parameters.get('region', 'us-east-1')
    
    print(f"Filtering findings: severity={severity}, limit={limit}, service={service_filter}, region={region}")
    
    # All available findings
    all_findings = [
        {
            "id": "finding-001",
            "title": "S3 bucket allows public read access",
            "severity": "CRITICAL",
            "service": "s3",
            "resource": "arn:aws:s3:::example-public-bucket",
            "region": "us-east-1",
            "remediation": "Remove public read access and use bucket policies"
        },
        {
            "id": "finding-002",
            "title": "EC2 security group allows unrestricted SSH",
            "severity": "HIGH", 
            "service": "ec2",
            "resource": "sg-0123456789abcdef0",
            "region": "us-east-1",
            "remediation": "Restrict SSH access to specific IP ranges"
        },
        {
            "id": "finding-003",
            "title": "RDS instance not encrypted",
            "severity": "HIGH",
            "service": "rds",
            "resource": "arn:aws:rds:us-east-1:123456789012:db:mydb",
            "region": "us-east-1", 
            "remediation": "Enable encryption at rest for RDS instance"
        },
        {
            "id": "finding-004",
            "title": "IAM user with unused access keys",
            "severity": "MEDIUM",
            "service": "iam",
            "resource": "arn:aws:iam::123456789012:user/old-user",
            "region": "global",
            "remediation": "Remove unused IAM access keys"
        },
        {
            "id": "finding-005",
            "title": "CloudTrail not enabled in region",
            "severity": "LOW",
            "service": "cloudtrail",
            "resource": "arn:aws:cloudtrail:us-west-2:123456789012:trail/missing",
            "region": "us-west-2",
            "remediation": "Enable CloudTrail in all regions"
        },
        {
            "id": "finding-006",
            "title": "Lambda function without dead letter queue",
            "severity": "LOW",
            "service": "lambda",
            "resource": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
            "region": "us-east-1",
            "remediation": "Configure dead letter queue for error handling"
        },
        {
            "id": "finding-007",
            "title": "EBS volume not encrypted",
            "severity": "MEDIUM",
            "service": "ec2",
            "resource": "vol-0123456789abcdef0",
            "region": "us-east-1",
            "remediation": "Enable EBS encryption for data at rest"
        }
    ]
    
    # Filter by severity
    if severity != 'ALL':
        filtered_findings = [f for f in all_findings if f['severity'] == severity]
    else:
        filtered_findings = all_findings
    
    # Filter by service if specified
    if service_filter:
        filtered_findings = [f for f in filtered_findings if service_filter in f['service']]
    
    # Filter by region if specified and not global
    if region != 'all':
        filtered_findings = [f for f in filtered_findings if f['region'] == region or f['region'] == 'global']
    
    # Apply limit
    limited_findings = filtered_findings[:limit]
    
    return {
        "findings": limited_findings,
        "total_found": len(filtered_findings),
        "total_available": len(all_findings),
        "filters_applied": {
            "severity": severity,
            "limit": limit,
            "service": service_filter or "all",
            "region": region
        }
    }

def get_security_services_filtered(parameters):
    """Return security services configuration for specified region"""
    region = parameters.get('region', 'us-east-1')
    service_filter = parameters.get('service', '').lower()
    
    print(f"Getting security services for region={region}, service={service_filter}")
    
    all_services = {
        "aws_security_hub": {
            "status": "ENABLED",
            "findings_count": 47,
            "compliance_score": 85,
            "region": region
        },
        "aws_guardduty": {
            "status": "ENABLED", 
            "threat_intel_sets": 3,
            "malware_protection": "ENABLED",
            "region": region
        },
        "aws_config": {
            "status": "ENABLED",
            "rules_count": 23,
            "compliant_resources": 156,
            "non_compliant_resources": 8,
            "region": region
        },
        "aws_cloudtrail": {
            "status": "ENABLED",
            "trails_count": 2,
            "data_events": "ENABLED",
            "region": region
        },
        "aws_inspector": {
            "status": "ENABLED",
            "assessments_count": 12,
            "findings_count": 34,
            "region": region
        }
    }
    
    # Filter by service if specified
    if service_filter:
        filtered_services = {k: v for k, v in all_services.items() if service_filter in k}
    else:
        filtered_services = all_services
    
    return {
        "region": region,
        "security_services": filtered_services,
        "filters_applied": {
            "region": region,
            "service_filter": service_filter or "all"
        },
        "recommendations": [
            f"Enable AWS Security Hub in additional regions beyond {region}",
            "Configure GuardDuty malware protection for S3",
            "Review and remediate Config non-compliant resources",
            "Enable CloudTrail insights for anomaly detection"
        ]
    }

def get_security_posture_filtered(parameters):
    """Return security posture analysis with optional recommendations"""
    include_recommendations = parameters.get('include_recommendations', 'true').lower() == 'true'
    region = parameters.get('region', 'us-east-1')
    
    print(f"Getting security posture: include_recommendations={include_recommendations}, region={region}")
    
    posture = {
        "overall_score": 78,
        "security_grade": "B+",
        "region": region,
        "last_assessment": "2025-10-19T19:57:00Z",
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
        },
        "filters_applied": {
            "include_recommendations": include_recommendations,
            "region": region
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
