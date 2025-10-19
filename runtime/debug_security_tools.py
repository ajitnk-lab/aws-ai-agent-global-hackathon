#!/usr/bin/env python3
"""
Debug script to test security tools in the same environment as AgentCore
"""
import os
import boto3
import json
from security_tools import SecurityAssessmentTools

def debug_environment():
    """Debug the runtime environment"""
    print("Environment Debug:")
    print(f"AWS_REGION: {os.getenv('AWS_REGION', 'Not set')}")
    print(f"AWS_DEFAULT_REGION: {os.getenv('AWS_DEFAULT_REGION', 'Not set')}")
    print(f"AWS_ACCESS_KEY_ID: {'Set' if os.getenv('AWS_ACCESS_KEY_ID') else 'Not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'Set' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'Not set'}")
    print(f"AWS_SESSION_TOKEN: {'Set' if os.getenv('AWS_SESSION_TOKEN') else 'Not set'}")
    
    # Test boto3 session
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        print(f"Boto3 credentials: {'Available' if credentials else 'Not available'}")
        
        # Get current region
        region = session.region_name
        print(f"Boto3 region: {region}")
        
        # Test Security Hub client
        client = session.client('securityhub')
        print(f"Security Hub client created successfully")
        
        # Test a simple call
        response = client.get_findings(MaxResults=1)
        print(f"Security Hub test call successful: {len(response['Findings'])} findings")
        
    except Exception as e:
        print(f"Boto3 error: {e}")

def debug_security_tools():
    """Debug SecurityAssessmentTools"""
    try:
        print("\nSecurityAssessmentTools Debug:")
        
        # Create tools instance
        tools = SecurityAssessmentTools(region='us-east-1')
        print(f"SecurityAssessmentTools created with region: {tools.region}")
        
        # Test get_security_findings with debug
        print("Calling get_security_findings...")
        result = tools.get_security_findings(limit=5)
        
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            print(f"Status: {result.get('status')}")
            print(f"Total findings: {result.get('total_findings')}")
            print(f"Filters applied: {result.get('filters_applied')}")
            
            findings = result.get('findings', [])
            print(f"Findings count: {len(findings)}")
            
            if findings:
                print("First finding:")
                print(json.dumps(findings[0], indent=2))
        
        return result
        
    except Exception as e:
        print(f"SecurityAssessmentTools error: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_security_hub_direct():
    """Debug Security Hub directly"""
    try:
        print("\nDirect Security Hub Debug:")
        
        client = boto3.client('securityhub', region_name='us-east-1')
        
        # Test with no filters
        response = client.get_findings(MaxResults=5)
        print(f"Direct call findings: {len(response['Findings'])}")
        
        if response['Findings']:
            finding = response['Findings'][0]
            print("Sample finding keys:", list(finding.keys()))
            print(f"Title: {finding.get('Title')}")
            print(f"Severity: {finding.get('Severity', {}).get('Label')}")
        
        return response
        
    except Exception as e:
        print(f"Direct Security Hub error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Security Tools Debug Script")
    print("=" * 60)
    
    debug_environment()
    debug_security_hub_direct()
    debug_security_tools()
