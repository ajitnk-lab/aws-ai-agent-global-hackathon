#!/usr/bin/env python3
"""
Direct test of Security Hub API to debug the issue
"""
import boto3
import json
from typing import Dict, List, Any, Optional

def test_security_hub_direct():
    """Test Security Hub API directly"""
    try:
        print("Testing Security Hub API directly...")
        
        # Create client
        client = boto3.client('securityhub', region_name='us-east-1')
        
        # Test basic get_findings call
        print("Calling get_findings with no filters...")
        response = client.get_findings(MaxResults=5)
        
        print(f"Response status: Success")
        print(f"Number of findings: {len(response['Findings'])}")
        
        if response['Findings']:
            print("Sample finding:")
            finding = response['Findings'][0]
            print(f"  Title: {finding.get('Title', 'Unknown')}")
            print(f"  Severity: {finding.get('Severity', {}).get('Label', 'Unknown')}")
            print(f"  Service: {finding.get('ProductName', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"Error calling Security Hub API: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_security_tools_class():
    """Test our SecurityAssessmentTools class"""
    try:
        print("\nTesting SecurityAssessmentTools class...")
        
        # Import our class
        import sys
        sys.path.append('/persistent/home/ubuntu/workspace/bedrockagent-agentcore-agentagetway/agentcore-security-app/runtime')
        from security_tools import SecurityAssessmentTools
        
        # Create instance
        tools = SecurityAssessmentTools(region='us-east-1')
        
        # Test get_security_findings
        print("Calling get_security_findings...")
        result = tools.get_security_findings(limit=5)
        
        print(f"Result status: {result.get('status', 'unknown')}")
        print(f"Total findings: {result.get('total_findings', 0)}")
        
        if result.get('findings'):
            print("Sample finding:")
            finding = result['findings'][0]
            print(f"  Title: {finding.get('title', 'Unknown')}")
            print(f"  Severity: {finding.get('severity', 'Unknown')}")
            print(f"  Service: {finding.get('service', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"Error with SecurityAssessmentTools: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Security Hub Direct Test")
    print("=" * 50)
    
    # Test direct API
    direct_success = test_security_hub_direct()
    
    # Test our class
    class_success = test_security_tools_class()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Direct API test: {'PASS' if direct_success else 'FAIL'}")
    print(f"SecurityTools class test: {'PASS' if class_success else 'FAIL'}")
