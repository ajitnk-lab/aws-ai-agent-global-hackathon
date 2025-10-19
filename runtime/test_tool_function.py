#!/usr/bin/env python3
"""
Test the exact tool function that AgentCore calls
"""
import json
from security_tools import SecurityAssessmentTools

# Initialize the same way as security_agent.py
security_tools = SecurityAssessmentTools(region='us-east-1')

def get_security_findings(severity_filter=None, limit=50, region=None, service_filter=None, resource_type=None, compliance_status=None):
    """Exact copy of the tool function"""
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

if __name__ == "__main__":
    print("=== TOOL FUNCTION TEST ===")
    
    # Test 1: No parameters (default call)
    print("\n1. Tool function with no parameters:")
    result = get_security_findings()
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(result)}")
    
    if isinstance(result, str) and result.startswith('{'):
        try:
            parsed = json.loads(result)
            print(f"Total findings: {parsed.get('total_findings', 'unknown')}")
            print(f"Status: {parsed.get('status', 'unknown')}")
        except:
            print("Failed to parse JSON result")
    else:
        print(f"Result preview: {result[:200]}...")
    
    # Test 2: With limit=5
    print("\n2. Tool function with limit=5:")
    result = get_security_findings(limit=5)
    if isinstance(result, str) and result.startswith('{'):
        try:
            parsed = json.loads(result)
            print(f"Total findings: {parsed.get('total_findings', 'unknown')}")
        except:
            print("Failed to parse JSON result")
    
    # Test 3: Direct SecurityAssessmentTools call for comparison
    print("\n3. Direct SecurityAssessmentTools call:")
    direct_result = security_tools.get_security_findings(limit=5)
    print(f"Direct total findings: {direct_result.get('total_findings', 'unknown')}")
    print(f"Direct status: {direct_result.get('status', 'unknown')}")
