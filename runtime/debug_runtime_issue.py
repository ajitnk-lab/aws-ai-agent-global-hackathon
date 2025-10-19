#!/usr/bin/env python3
"""
Debug the AgentCore runtime vs direct call discrepancy
"""
import boto3
import json
import os
from security_tools import SecurityAssessmentTools

def test_runtime_environment():
    """Test the exact same calls in runtime environment"""
    print("=== RUNTIME ENVIRONMENT DEBUG ===")
    
    # Test 1: Direct Security Hub API call
    print("\n1. Direct Security Hub API call:")
    try:
        client = boto3.client('securityhub', region_name='us-east-1')
        response = client.get_findings(MaxResults=5)
        print(f"   ✅ Direct API: {len(response['Findings'])} findings")
    except Exception as e:
        print(f"   ❌ Direct API error: {e}")
    
    # Test 2: SecurityAssessmentTools class
    print("\n2. SecurityAssessmentTools class:")
    try:
        tools = SecurityAssessmentTools(region='us-east-1')
        result = tools.get_security_findings(limit=5)
        print(f"   ✅ SecurityTools: {result.get('total_findings', 0)} findings")
        print(f"   Status: {result.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ SecurityTools error: {e}")
    
    # Test 3: Check _get_security_hub_findings directly
    print("\n3. _get_security_hub_findings method:")
    try:
        tools = SecurityAssessmentTools(region='us-east-1')
        findings = tools._get_security_hub_findings(None, None, 'us-east-1', None, None, 5)
        print(f"   ✅ _get_security_hub_findings: {len(findings)} findings")
        if findings:
            print(f"   First finding: {findings[0].title}")
    except Exception as e:
        print(f"   ❌ _get_security_hub_findings error: {e}")
    
    # Test 4: Check environment variables
    print("\n4. Environment check:")
    print(f"   AWS_REGION: {os.getenv('AWS_REGION', 'Not set')}")
    print(f"   AWS_DEFAULT_REGION: {os.getenv('AWS_DEFAULT_REGION', 'Not set')}")
    
    # Test 5: Check boto3 session
    print("\n5. Boto3 session check:")
    try:
        session = boto3.Session()
        print(f"   Region: {session.region_name}")
        creds = session.get_credentials()
        print(f"   Credentials: {'Available' if creds else 'Not available'}")
    except Exception as e:
        print(f"   ❌ Session error: {e}")

if __name__ == "__main__":
    test_runtime_environment()
