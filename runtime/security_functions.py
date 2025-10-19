"""
Standalone security functions for Lambda without AgentCore dependencies
"""
import json
from security_tools import SecurityAssessmentTools

# Initialize security tools
security_tools = SecurityAssessmentTools()

def get_security_findings(severity_filter=None, limit=50, region=None, service_filter=None, resource_type=None, compliance_status=None):
    """Retrieve security findings from AWS services with comprehensive filtering"""
    try:
        result = security_tools.get_security_findings(
            severity_filter=severity_filter,
            limit=limit,
            region=region,
            service_filter=service_filter,
            resource_type=resource_type,
            compliance_status=compliance_status
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting security findings: {str(e)}"

def check_security_services():
    """Monitor AWS security services operational status across your infrastructure"""
    try:
        result = security_tools.check_security_services()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error checking security services: {str(e)}"

def analyze_security_posture():
    """Comprehensive security posture analysis against AWS Well-Architected Framework"""
    try:
        result = security_tools.analyze_security_posture()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error analyzing security posture: {str(e)}"
